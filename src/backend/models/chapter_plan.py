  
# Chapter_Plans (ID, Chapter_ID, Content)
# Users (ID, Name)


from sqlalchemy import Column, String, Integer, ForeignKey,Enum
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Chapter_Plan(BaseModel):
    __tablename__ = "chapter_plans"

    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"),nullable=False)  
    content = Column(String, nullable=False)
   

    chapter = relationship(
        "Chapter", back_populates="chapter_plan"
    )
  