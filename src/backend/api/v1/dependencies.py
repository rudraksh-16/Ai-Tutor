# src/backend/api/v1/dependencies.py — Shared FastAPI Dependencies

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.common.exceptions import EntityNotFoundError
from src.backend.models.user import User
from src.backend.models.topic import Topic
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.repository.chapter_repo import chapter_repo
from src.backend.repository.topic_repo import topic_repo
from src.backend.schemas.chapter import ChapterRead


async def verify_chapter_ownership(
    db: AsyncSession, chapter_id: UUID, current_user: User
) -> ChapterRead:
    """Verify that the current user owns the topic containing this chapter.

    Args:
        db: Database session.
        chapter_id: Target chapter ID.
        current_user: Authenticated user.

    Returns:
        The matched Chapter matching the schema.

    Raises:
        EntityNotFoundError: If chapter is missing.
        HTTPException: If unauthorized.
    """
    chapter_obj = await chapter_repo.get(db, chapter_id)
    if not chapter_obj:
        raise EntityNotFoundError(f"Chapter not found: {chapter_id}")

    topic_obj = await topic_repo.get(db, chapter_obj.topic_id)
    if not topic_obj or str(topic_obj.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this chapter"
        )
    return chapter_obj


async def verify_section_ownership(
    db: AsyncSession, section_id: UUID, current_user: User
) -> ChapterPlan:
    """Verify that the current user owns the topic containing this section/sub-chapter.

    Args:
        db: Database session.
        section_id: Target section (ChapterPlan) ID.
        current_user: Authenticated user.

    Returns:
        The matched ChapterPlan model.

    Raises:
        EntityNotFoundError: If section is missing.
        HTTPException: If unauthorized.
    """
    res = await db.execute(select(ChapterPlan).filter(ChapterPlan.id == section_id))
    section = res.scalars().first()
    if not section:
        raise EntityNotFoundError(f"Section not found: {section_id}")

    # Re-use chapter ownership logic to verify the parent chain
    await verify_chapter_ownership(db, section.chapter_id, current_user)
    return section


async def verify_topic_ownership(
    db: AsyncSession, topic_id: UUID, current_user: User
) -> Topic:
    """Verify that the current user owns the target topic.

    Args:
        db: Database session.
        topic_id: Target topic ID.
        current_user: Authenticated user.

    Returns:
        The matched Topic model.

    Raises:
        EntityNotFoundError: If topic is missing.
        HTTPException: If unauthorized.
    """
    topic_obj = await topic_repo.get(db, topic_id)
    if not topic_obj:
        raise EntityNotFoundError(f"Topic not found: {topic_id}")
    
    if str(topic_obj.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this topic"
        )
    return topic_obj
