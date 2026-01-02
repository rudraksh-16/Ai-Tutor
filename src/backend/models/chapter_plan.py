
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel


class ChapterPlan(BaseModel):
    __tablename__ = "chapter_plans"

    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"),nullable=False)  
    content = Column(Text, nullable=False)
   

    chapter = relationship(
        "Chapter", back_populates="chapter_plan"
    )
  