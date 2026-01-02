from sqlalchemy import Column, String, Integer, ForeignKey,Enum, Text
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Chapter(BaseModel):
    __tablename__ = "chapters"

    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"),nullable=False)  
    title = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)  
    status = Column(Enum(Status), nullable=False)
    outline = Column(Text, nullable=False)
   
    chapter_plan = relationship("ChapterPlan",back_populates="chapter",cascade="all, delete-orphan")

    topic = relationship(
        "Topic", back_populates="chapters"
    )
  