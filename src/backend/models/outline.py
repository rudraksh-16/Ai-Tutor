from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Outline(BaseModel):
    __tablename__ = "outlines"

    chapter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        
    )

    title = Column(String, nullable=False)
    status = Column(
        Enum(Status, values_callable=lambda e: [member.value for member in e]),
        nullable=False,
        default=Status.PENDING.value,
    )
    sequence = Column(Integer, nullable=False)
    context = Column(Text, nullable=False)

    chapter = relationship("Chapter", back_populates="outlines")
    outline_plan = relationship(
        "OutlinePlan",
        back_populates="outline",
        cascade="all, delete-orphan",
    )
