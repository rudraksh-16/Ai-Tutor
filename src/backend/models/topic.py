from sqlalchemy import Column, String, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel
from src.backend.enums.status import TopicStatus


class Topic(BaseModel):
    __tablename__ = "topics"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    user_summary = Column(Text, nullable=False)
    curriculum_text = Column(Text, nullable=True)
    status = Column(
        Enum(TopicStatus, values_callable=lambda e: [member.value for member in e]),
        nullable=False,
        default=TopicStatus.PENDING.value,
    )

    user = relationship("User", back_populates="topics")
    chapters = relationship(
        "Chapter",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="Chapter.order_index",
        lazy="selectin",
    )
