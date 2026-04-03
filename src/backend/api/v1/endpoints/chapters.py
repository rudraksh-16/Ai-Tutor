from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.common.exceptions import EntityNotFoundError
from src.backend.db.database import get_db
from src.backend.enums.status import ChapterStatus
from src.backend.models.user import User
from src.backend.repository.chapter_repo import chapter_repo
from src.backend.repository.topic_repo import topic_repo
from src.backend.schemas.chapter import ChapterRead

router = APIRouter()


async def verify_chapter_ownership(
    db: AsyncSession, chapter_id: UUID, current_user: User
) -> ChapterRead:
    chapter_obj = await chapter_repo.get(db, chapter_id)
    if not chapter_obj:
        raise EntityNotFoundError(f"Chapter not found: {chapter_id}")

    topic_obj = await topic_repo.get(db, chapter_obj.topic_id)
    if not topic_obj or str(topic_obj.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return chapter_obj


@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)
    return chapter_obj


@router.post("/{chapter_id}/complete", response_model=ChapterRead)
async def complete_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChapterRead:
    """Mark a chapter as completed (after quiz pass) and unlock the next one."""
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)

    updated_chapter = await chapter_repo.update(
        db, chapter_obj, {"status": ChapterStatus.COMPLETED.value}
    )

    # Unlock next chapter to PENDING (accessible but not started)
    next_chapter = await chapter_repo.get_next_chapter(
        db, chapter_obj.topic_id, chapter_obj.order_index
    )
    if next_chapter:
        await chapter_repo.update(db, next_chapter, {"status": ChapterStatus.PENDING.value})

    return updated_chapter
