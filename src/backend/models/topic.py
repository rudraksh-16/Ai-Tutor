from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Topic(BaseModel):
    __tablename__ = "topics"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    user_summary = Column(Text, nullable=False)

    user = relationship("User", back_populates="topics")
    chapters = relationship(
        "Chapter",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="Chapter.sequence",
    )
