import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.api.auth.utils import get_current_user
from src.backend.api.v1.dependencies import verify_topic_ownership
from src.backend.common.exceptions import EntityNotFoundError
from src.backend.db.database import get_db
from src.backend.models.user import User
from src.backend.repository.chapter_repo import chapter_repo
from src.backend.repository.topic_repo import topic_repo
from src.backend.repository.planner_repo import planner_repo
from src.backend.schemas.chapter import ChapterRead
from src.backend.schemas.topic import TopicCreate, TopicRead

logger = logging.getLogger(__name__)

router = APIRouter()


class TopicStartRequest(BaseModel):
    title: str
    user_summary: str


class PlanningStatusResponse(BaseModel):
    topic_status: str
    total_chapters: int
    planned_chapters: int
    planning_complete: bool


@router.post("/", response_model=TopicRead)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TopicRead:
    """Create a new topic record. Forced user_id check."""
    if str(current_user.id) != str(topic_in.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden: Cannot create topic for another user"
        )
    return await topic_repo.create(
        db, 
        {"title": topic_in.title, "user_summary": topic_in.user_summary, "user_id": topic_in.user_id}
    )


@router.post("/start", response_model=TopicRead)
async def start_topic(
    request: TopicStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TopicRead:
    """Simplified topic creation from the UI: user_id from auth token."""
    return await topic_repo.create(
        db, {
            "title": request.title,
            "user_summary": request.user_summary,
            "user_id": current_user.id,
        }
    )


@router.get("/{topic_id}", response_model=TopicRead)
async def get_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TopicRead:
    """Fetch a single topic by ID. Verified ownership."""
    # Re-use centralized ownership check
    topic_obj = await verify_topic_ownership(db, topic_id, current_user)
    return topic_obj


@router.get("/{topic_id}/chapters", response_model=List[ChapterRead])
async def get_topic_chapters(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ChapterRead]:
    """Fetch all chapters for a specific topic. Verified ownership."""
    await verify_topic_ownership(db, topic_id, current_user)
    return await chapter_repo.get_by_topic(db, topic_id)


@router.get("/{topic_id}/status", response_model=PlanningStatusResponse)
async def get_planning_status(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlanningStatusResponse:
    """Get the planning progress for a topic. Verified ownership."""
    topic_obj = await verify_topic_ownership(db, topic_id, current_user)

    chapters = await chapter_repo.get_by_topic(db, topic_id)
    planned = 0
    for ch in chapters:
        if await planner_repo.sections_exist(db, ch.id):
            planned += 1

    return PlanningStatusResponse(
        topic_status=str(topic_obj.status.value) if hasattr(topic_obj.status, 'value') else str(topic_obj.status),
        total_chapters=len(chapters),
        planned_chapters=planned,
        planning_complete=len(chapters) > 0,
    )
