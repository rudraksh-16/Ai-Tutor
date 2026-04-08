from typing import List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.quiz_question import QuizQuestion
from src.backend.repository.base_repo import BaseRepository


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self):
        super().__init__(QuizQuestion)

    async def get_by_section(
        self, db: AsyncSession, section_id: UUID
    ) -> List[QuizQuestion]:
        """Fetch all quiz questions for a specific section."""
        result = await db.execute(
            select(self.model).filter(
                self.model.section_id == section_id,
                self.model.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def save_batch(
        self, db: AsyncSession, chapter_id: UUID, questions: List[dict], section_id: UUID = None
    ) -> List[QuizQuestion]:
        """Bulk insert quiz questions for a chapter or section."""
        db_objects = []
        for q in questions:
            obj = QuizQuestion(
                chapter_id=chapter_id,
                section_id=section_id,
                question_text=q["question_text"],
                question_type=q.get("question_type", "mcq"),
                options=q.get("options"),
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
            )
            db.add(obj)
            db_objects.append(obj)
        await db.commit()
        for obj in db_objects:
            await db.refresh(obj)
        return db_objects

    async def delete_by_section(self, db: AsyncSession, section_id: UUID) -> None:
        """Hard-delete all quiz questions for a section before regeneration."""
        await db.execute(
            delete(self.model).where(self.model.section_id == section_id)
        )
        await db.commit()

    async def delete_by_chapter(self, db: AsyncSession, chapter_id: UUID) -> None:
        """Hard-delete all quiz questions for a chapter before regeneration."""
        await db.execute(
            delete(self.model).where(self.model.chapter_id == chapter_id)
        )
        await db.commit()


quiz_question_repo = QuizQuestionRepository()
