from sqlalchemy import Column, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class QuizAttempt(BaseModel):
    __tablename__ = "quiz_attempts"
    __table_args__ = (
        Index("ix_quiz_attempts_chapter_user", "chapter_id", "user_id"),
    )

    chapter_id = Column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    section_id = Column(
        UUID(as_uuid=True), ForeignKey("chapter_plans.id", ondelete="CASCADE"), nullable=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)

    chapter = relationship("Chapter", backref="quiz_attempts")
    user = relationship("User", backref="quiz_attempts")
