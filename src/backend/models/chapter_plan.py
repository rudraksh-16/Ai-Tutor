from sqlalchemy import Column, ForeignKey, Text, Integer,Enum,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.backend.enums.status import Status
from src.backend.models.base import BaseModel


class ChapterPlan(BaseModel):
    __tablename__ = "chapter_plans"
    title = Column(String, nullable=False)
    chapter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(
        Enum(Status, values_callable=lambda e: [member.value for member in e]),
        nullable=False,
        default=Status.PENDING.value,
    )
    sequence = Column(Integer,nullable=False)
    content = Column(Text, nullable=False)

    chapter = relationship("Chapter", back_populates="chapter_plan")