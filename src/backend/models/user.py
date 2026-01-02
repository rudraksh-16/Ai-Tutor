from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from src.backend.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)

    curriculums = relationship(
        "Curriculum", back_populates="user", cascade="all, delete-orphan"
    )
