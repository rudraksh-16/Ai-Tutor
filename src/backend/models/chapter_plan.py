from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class ChapterPlan(BaseModel):
    __tablename__ = "chapter_plans"

    chapter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)

    chapter = relationship("Chapter", back_populates="chapter_plan")
