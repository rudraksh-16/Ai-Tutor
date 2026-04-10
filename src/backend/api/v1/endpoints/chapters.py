from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.common.exceptions import EntityNotFoundError
from src.backend.db.database import get_db
from src.backend.enums.status import ChapterStatus
from src.backend.models.user import User
from src.backend.repository.chapter_repo import chapter_repo
from src.backend.repository.message_repo import message_repo
from src.backend.repository.quiz_attempt_repo import quiz_attempt_repo
from src.backend.repository.topic_repo import topic_repo
from src.backend.schemas.chapter import ChapterRead
from src.backend.services.teacher_service import TeacherService

router = APIRouter()
PASS_THRESHOLD = 0.7


class QuizFeedbackItem(BaseModel):
    question_id: str
    selected_option: Optional[str] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    is_correct: bool


class QuizStatePayload(BaseModel):
    quiz_key: str
    selected_answers: Dict[str, str] = Field(default_factory=dict)
    submitted: bool = False
    score: Optional[int] = None
    total: Optional[int] = None
    passed: Optional[bool] = None
    feedback: List[QuizFeedbackItem] = Field(default_factory=list)


class QuizStateResponse(BaseModel):
    quiz_key: str
    selected_answers: Dict[str, str] = Field(default_factory=dict)
    submitted: bool = False
    score: Optional[int] = None
    total: Optional[int] = None
    passed: Optional[bool] = None
    feedback: List[QuizFeedbackItem] = Field(default_factory=list)
    chapter_status: Optional[str] = None
    saved_at: Optional[str] = None


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


@router.get("/{chapter_id}/quiz-state", response_model=Optional[QuizStateResponse])
async def get_quiz_state(
    chapter_id: UUID,
    quiz_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[QuizStateResponse]:
    """Return the latest persisted quiz state for the teacher-generated quiz."""
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)
    conversation = await TeacherService.get_or_create_conversation(db, current_user.id, chapter_id)
    state_message = await message_repo.get_latest_quiz_state(db, conversation.id, quiz_key)

    if not state_message or not state_message.meta:
        return None

    meta = state_message.meta
    return QuizStateResponse(
        quiz_key=meta.get("quiz_key", quiz_key),
        selected_answers=meta.get("selected_answers", {}),
        submitted=meta.get("submitted", False),
        score=meta.get("score"),
        total=meta.get("total"),
        passed=meta.get("passed"),
        feedback=meta.get("feedback", []),
        chapter_status=chapter_obj.status.value if hasattr(chapter_obj.status, "value") else str(chapter_obj.status),
        saved_at=state_message.updated_at.isoformat() if state_message.updated_at else None,
    )


@router.put("/{chapter_id}/quiz-state", response_model=QuizStateResponse)
async def save_quiz_state(
    chapter_id: UUID,
    payload: QuizStatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizStateResponse:
    """Persist quiz draft answers and submitted quiz results for the teacher flow."""
    chapter_obj = await verify_chapter_ownership(db, chapter_id, current_user)
    conversation = await TeacherService.get_or_create_conversation(db, current_user.id, chapter_id)

    state_payload: Dict[str, Any] = {
        "selected_answers": payload.selected_answers,
        "submitted": payload.submitted,
        "score": payload.score,
        "total": payload.total,
        "passed": payload.passed,
        "feedback": [item.model_dump() for item in payload.feedback],
    }

    computed_passed = payload.passed
    if payload.submitted:
        total = payload.total or 0
        score = payload.score or 0
        computed_passed = (score / total) >= PASS_THRESHOLD if total > 0 else False
        state_payload["passed"] = computed_passed

    state_message = await message_repo.save_quiz_state(
        db,
        conversation.id,
        payload.quiz_key,
        state_payload,
    )

    if payload.submitted:
        await quiz_attempt_repo.create(
            db,
            {
                "chapter_id": chapter_id,
                "user_id": current_user.id,
                "score": payload.score or 0,
                "total_questions": payload.total or 0,
                "passed": bool(computed_passed),
            },
        )

        if computed_passed and chapter_obj.status != ChapterStatus.COMPLETED:
            await TeacherService.update_status(db, chapter_id, "complete")
            chapter_obj = await chapter_repo.get(db, chapter_id)

    return QuizStateResponse(
        quiz_key=payload.quiz_key,
        selected_answers=payload.selected_answers,
        submitted=payload.submitted,
        score=payload.score,
        total=payload.total,
        passed=computed_passed,
        feedback=payload.feedback,
        chapter_status=chapter_obj.status.value if hasattr(chapter_obj.status, "value") else str(chapter_obj.status),
        saved_at=state_message.updated_at.isoformat() if state_message.updated_at else None,
    )
