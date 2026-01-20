from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class OutlinePlan(BaseModel):
    __tablename__ = "outline_plans"

    outline_id = Column(
        UUID(as_uuid=True),
        ForeignKey("outlines.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)

    outline = relationship("Outline", back_populates="outline_plan")
