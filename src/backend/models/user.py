from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)

    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
