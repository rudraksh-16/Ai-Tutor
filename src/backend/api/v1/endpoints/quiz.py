import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.api.v1.dependencies import verify_chapter_ownership, verify_section_ownership
from src.backend.db.database import get_db
from src.backend.models.user import User
from src.backend.schemas.quiz import (
    QuizQuestionRead,
    QuizResultResponse,
    QuizSubmissionRequest,
)
from src.backend.services.quiz_validation_service import quiz_validation_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{chapter_id}",
    response_model=List[QuizQuestionRead],
)
async def get_quiz_questions(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[QuizQuestionRead]:
    """Fetch chapter-level quiz questions WITHOUT correct answers."""
    await verify_chapter_ownership(db, chapter_id, current_user)
    return await quiz_validation_service.get_questions_for_user(db, chapter_id)


# ─── Section Level Routes ───

@router.get(
    "/section/{section_id}",
    response_model=List[QuizQuestionRead],
)
async def get_section_quiz_questions(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[QuizQuestionRead]:
    """Fetch section-level quiz questions WITHOUT correct answers."""
    section = await verify_section_ownership(db, section_id, current_user)
    return await quiz_validation_service.get_questions_for_user(db, section.chapter_id, section_id)


@router.post(
    "/section/{section_id}/generate",
    response_model=List[QuizQuestionRead],
)
async def generate_section_quiz(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[QuizQuestionRead]:
    """Trigger AI generation of a specialized quiz for this specific section."""
    await verify_section_ownership(db, section_id, current_user)
    return await quiz_validation_service.generate_section_quiz(db, section_id)


@router.post(
    "/{chapter_id}/submit",
    response_model=QuizResultResponse,
)
async def submit_quiz(
    chapter_id: UUID,
    request: QuizSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizResultResponse:
    """Submit chapter-level quiz answers for validation."""
    await verify_chapter_ownership(db, chapter_id, current_user)
    return await quiz_validation_service.validate_and_record(
        db, chapter_id, current_user.id, request.answers,
    )


@router.post(
    "/section/{section_id}/submit",
    response_model=QuizResultResponse,
)
async def submit_section_quiz(
    section_id: UUID,
    request: QuizSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizResultResponse:
    """Submit section-level quiz answers for validation and progression."""
    section = await verify_section_ownership(db, section_id, current_user)
    return await quiz_validation_service.validate_and_record(
        db, section.chapter_id, current_user.id, request.answers, section_id
    )
