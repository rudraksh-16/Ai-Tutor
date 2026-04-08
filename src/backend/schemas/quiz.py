from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuizQuestionRead(BaseModel):
    """Public schema — excludes correct_answer and explanation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question_text: str
    question_type: str
    options: Optional[List[str]] = None


class AnswerItem(BaseModel):
    """A single answer submitted by the user."""

    question_id: UUID
    selected_option: str


class QuizSubmissionRequest(BaseModel):
    """Payload for submitting quiz answers."""

    answers: List[AnswerItem]


class QuestionFeedback(BaseModel):
    """Per-question feedback returned after submission."""

    question_id: UUID
    question_text: str
    selected_option: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class QuizResultResponse(BaseModel):
    """Result returned after quiz submission."""

    score: int
    total: int
    passed: bool
    feedback: List[QuestionFeedback]
