from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"

    sender_id = Column(UUID(as_uuid=True), nullable=False)

    sender_role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    chapter = relationship("Chapter", back_populates="chapter_plan")
