from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel

class Curriculum(BaseModel):
    __tablename__ = "curriculums"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    title = Column(String, nullable=False)
    user_summary = Column(String, nullable=False)
    plan = Column(String, nullable=False)

    user = relationship("User", back_populates="curriculums")
    chapters = relationship(
        "Chapter", back_populates="curriculum", cascade="all, delete-orphan",order_by="Chapter.sequence_order"
    )

