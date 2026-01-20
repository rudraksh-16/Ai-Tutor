from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.backend.models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_conversation = relationship("User", back_populates="conversations")
    contents = relationship(
        "ConversationContent",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
