from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Chapter(BaseModel):
    __tablename__ = "chapters"

    topic_id = Column(
        UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    status = Column(
        Enum(Status, values_callable=lambda e: [member.value for member in e]),
        nullable=False,
        default=Status.PENDING.value,
    )
    outline = Column(Text, nullable=False)

    outlines = relationship(
        "Outline",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Outline.sequence",
    )
    topic = relationship("Topic", back_populates="chapters")
