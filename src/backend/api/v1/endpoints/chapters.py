from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.db.database import get_db
from src.backend.api.v1.dependencies import verify_chapter_ownership
from src.backend.models.user import User
from src.backend.schemas.chapter import ChapterRead
from src.backend.services.quiz_validation_service import quiz_validation_service

router = APIRouter()


@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Fetch a single chapter's details. Verified ownership."""
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)
    return chapter_obj


@router.post("/{chapter_id}/complete", response_model=ChapterRead)
async def complete_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Mark a chapter as completed and unlock the next one.
    
    This endpoint delegates logic to the QuizValidationService to ensure
    consistency between manual and automated completions.
    """
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)

    # Delegate completion logic to service (DIP/DRY compliant)
    await quiz_validation_service.mark_chapter_completed(db, chapter_id)
    
    # Re-fetch to show updated status
    return await verify_chapter_ownership(db, chapter_id, current_user)
