import logging
from typing import List, Union
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.api.v1.endpoints.chapters import verify_chapter_ownership
from src.backend.db.database import get_db
from src.backend.models.user import User
from src.backend.schemas.section import SectionRead
from src.backend.services.planner_service import PlannerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{chapter_id}/document",
    response_model=List[SectionRead],
)
async def get_chapter_document(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch or JIT-generate the structured sections for a chapter.

    Returns:
        200 with sections if ready.
        202 with {"status": "generating"} if generation is in progress.
        500 if generation failed (triggers UI retry).
    """
    await verify_chapter_ownership(db, chapter_id, current_user)
    
    # Check current status before potential generation trigger
    from src.backend.repository.chapter_repo import chapter_repo
    from src.backend.enums.status import ChapterStatus
    chapter = await chapter_repo.get(db, chapter_id)
    if chapter and chapter.status == ChapterStatus.FAILED:
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "message": "AI generation failed for this chapter. Please retry."}
        )

    try:
        sections = await PlannerService.get_or_generate_sections(db, chapter_id, current_user)
    except ValueError as e:
        return JSONResponse(
            status_code=429,
            content={"status": "rate_limited", "message": str(e)}
        )

    if sections is None:
        return JSONResponse(
            status_code=202,
            content={"status": "generating", "message": "Sections are being generated. Poll again shortly."},
        )

    return sections


@router.post("/{chapter_id}/generate")
async def trigger_chapter_generation(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger background content generation for a specific chapter.

    This allows users to pre-generate chapter content from the overview
    panel without navigating into the reading view.

    Returns:
        200 with current status if already generated or generating.
        200 with 'generating' if successfully triggered.
        403 if the chapter is locked.
    """
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)

    current_status = (chapter_obj.status.value
                      if hasattr(chapter_obj.status, 'value')
                      else str(chapter_obj.status)).lower()

    # Pre-generation is allowed even if the chapter is 'locked' to the reader
    # but already exists in the course plan (pending / not_started / failed)
    if current_status in ('in_progress', 'completed', 'quiz_pending'):
        return {"status": current_status, "message": "Content already available."}

    if current_status == 'generating':
        return {"status": "generating", "message": "Generation already in progress."}

    # Trigger generation (locked / pending / not_started / failed)
    try:
        sections = await PlannerService.get_or_generate_sections(db, chapter_id, current_user)
    except ValueError as rate_err:
        return JSONResponse(
            status_code=429,
            content={"status": "rate_limited", "message": str(rate_err)},
        )

    if sections is None:
        return {"status": "generating", "message": "Generation started in the background."}

    return {"status": "in_progress", "message": "Content is ready."}


@router.post("/{chapter_id}/retry")
async def retry_chapter_generation(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reset a FAILED or stuck chapter and re-trigger generation."""
    await verify_chapter_ownership(db, chapter_id, current_user)
    
    success = await PlannerService.reset_chapter_for_retry(db, chapter_id)
    if not success:
        return JSONResponse(status_code=404, content={"message": "Chapter not found"})
        
    return {"status": "success", "message": "Chapter reset. It will be re-generated on next access."}
