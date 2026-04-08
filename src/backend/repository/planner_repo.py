import logging
from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.models.topic import Topic

logger = logging.getLogger(__name__)


class PlannerRepository:
    """Handles data operations for the chapter planner."""

    @staticmethod
    async def get_chapter_with_context(
        db: AsyncSession, chapter_id: UUID
    ) -> object:
        """Fetch a single chapter with its topic context for JIT planning.

        Returns a row with: chapter_id, chapter_title, description,
        topic_title, user_summary, all_chapters_text.
        """
        chapter_result = await db.execute(
            select(Chapter).filter(Chapter.id == chapter_id, Chapter.deleted_at.is_(None))
        )
        chapter = chapter_result.scalars().first()
        if not chapter:
            return None

        topic_result = await db.execute(
            select(Topic).filter(Topic.id == chapter.topic_id)
        )
        topic = topic_result.scalars().first()

        all_chapters_result = await db.execute(
            select(Chapter)
            .filter(Chapter.topic_id == chapter.topic_id, Chapter.deleted_at.is_(None))
            .order_by(Chapter.order_index)
        )
        all_chapters = all_chapters_result.scalars().all()
        all_chapters_text = "\n".join(f"- {c.title}" for c in all_chapters)

        return _ChapterContext(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            description=chapter.description,
            topic_title=topic.title,
            user_summary=topic.user_summary,
            all_chapters_text=all_chapters_text,
        )

    @staticmethod
    async def sections_exist(db: AsyncSession, chapter_id: UUID) -> bool:
        """Check if sections already exist (with row-level lock to prevent races)."""
        result = await db.execute(
            select(ChapterPlan.id)
            .filter(ChapterPlan.chapter_id == chapter_id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        return result.scalars().first() is not None

    @staticmethod
    async def insert_sections(
        db: AsyncSession, chapter_id: UUID, sections: List[Dict[str, str]]
    ) -> None:
        """Batch-insert multiple ChapterPlan rows for one chapter.
        
        Note: The caller is responsible for committing the transaction.
        """
        for index, section in enumerate(sections):
            db.add(ChapterPlan(
                chapter_id=chapter_id,
                title=section["title"],
                content=section["content"],
                order_index=index,
            ))
        await db.flush()
        logger.info("Added %d sections to session for chapter %s.", len(sections), chapter_id)

    @staticmethod
    async def get_sections(
        db: AsyncSession, chapter_id: UUID
    ) -> List[ChapterPlan]:
        """Fetch all sections for a chapter sorted by order_index."""
        result = await db.execute(
            select(ChapterPlan)
            .filter(ChapterPlan.chapter_id == chapter_id)
            .order_by(ChapterPlan.order_index)
        )
        return list(result.scalars().all())


class _ChapterContext:
    """Simple data container for chapter context passed to the Planner."""

    __slots__ = (
        "chapter_id", "chapter_title", "description",
        "topic_title", "user_summary", "all_chapters_text",
    )

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


planner_repo = PlannerRepository()
