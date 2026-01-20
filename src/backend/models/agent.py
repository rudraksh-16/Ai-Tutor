from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel


class Agent(BaseModel):
    __tablename__ = "agents"

    name = Column(String, nullable=False)
