from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel
from src.backend.enums.status import ChapterStatus


class Chapter(BaseModel):
    __tablename__ = "chapters"
    __table_args__ = (
        Index("ix_chapters_topic_order", "topic_id", "order_index"),
    )

    topic_id = Column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        Enum(ChapterStatus, values_callable=lambda e: [member.value for member in e]),
        nullable=False,
        default=ChapterStatus.LOCKED.value,
    )

    chapter_plans = relationship(
        "ChapterPlan",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="ChapterPlan.order_index",
        lazy="selectin",
    )

    topic = relationship("Topic", back_populates="chapters")
