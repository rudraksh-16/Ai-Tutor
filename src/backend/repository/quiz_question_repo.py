from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.quiz_question import QuizQuestion
from src.backend.repository.base_repo import BaseRepository


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self):
        super().__init__(QuizQuestion)

    async def get_by_chapter(
        self, db: AsyncSession, chapter_id: UUID
    ) -> List[QuizQuestion]:
        result = await db.execute(
            select(self.model).filter(
                self.model.chapter_id == chapter_id,
                self.model.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())


quiz_question_repo = QuizQuestionRepository()
