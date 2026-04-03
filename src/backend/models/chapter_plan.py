from sqlalchemy import Column, ForeignKey, Text, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class ChapterPlan(BaseModel):
    __tablename__ = "chapter_plans"
    __table_args__ = (
        Index("ix_chapter_plans_chapter_order", "chapter_id", "order_index"),
    )

    title = Column(String, nullable=False)
    chapter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    chapter = relationship("Chapter", back_populates="chapter_plans")
