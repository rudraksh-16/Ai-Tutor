from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SectionRead(BaseModel):
    """Public schema for a chapter section (sub-topic)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    order_index: int
    is_completed: bool
    chapter_id: UUID
    created_at: datetime
    updated_at: datetime
