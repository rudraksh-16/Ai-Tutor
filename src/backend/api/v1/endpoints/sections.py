import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.common.exceptions import EntityNotFoundError
from src.backend.db.database import get_db
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.patch("/{section_id}/read")
async def mark_section_read(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Mark a chapter section (sub-topic) as read by the user."""
    from src.backend.api.v1.dependencies import verify_section_ownership
    section = await verify_section_ownership(db, section_id, current_user)

    section.is_completed = True
    await db.commit()
    logger.info("Section %s marked as read.", section_id)

    return {"status": "success", "section_id": str(section_id), "is_completed": True}
