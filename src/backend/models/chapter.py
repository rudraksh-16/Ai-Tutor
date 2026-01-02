from sqlalchemy import Column, String, Integer, ForeignKey,Enum
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel
from src.backend.enums.status import Status


class Chapter(BaseModel):
    __tablename__ = "chapters"

    curriculum_id = Column(Integer, ForeignKey("curriculums.id", ondelete="CASCADE"),nullable=False)
    sequence_order = Column(Integer, nullable=False)    
    title = Column(String, nullable=False)
    status = Column(Enum(Status), nullable=False)
    content = Column(String, nullable=False)
   

    curriculum = relationship(
        "Curriculum", back_populates="chapters"
    )
