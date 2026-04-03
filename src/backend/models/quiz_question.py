from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.backend.models.base import BaseModel


class QuizQuestion(BaseModel):
    __tablename__ = "quiz_questions"

    chapter_id = Column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # "mcq" or "open"
    options = Column(JSONB, nullable=True)  # For MCQ: ["A) ...", "B) ...", ...]
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)

    chapter = relationship("Chapter", backref="quiz_questions")
