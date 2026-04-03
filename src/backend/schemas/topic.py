from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime
from src.backend.enums.status import TopicStatus
from src.backend.schemas.chapter import ChapterRead


class TopicBase(BaseModel):
    title: str
    user_summary: str


class TopicCreate(TopicBase):
    user_id: UUID4


class TopicRead(TopicBase):
    id: UUID4
    user_id: UUID4
    status: TopicStatus
    curriculum_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chapters: List[ChapterRead] = []

    class Config:
        from_attributes = True
