import enum
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship

from src.backend.models.base import BaseModel


class UserStatus(enum.Enum):
    INVITED = "invited"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Null for invited users
    is_verified = Column(Boolean, default=True) # Automatically verified for now
    status = Column(
        Enum(UserStatus, name="userstatus", values_callable=lambda x: [e.value for e in x]), 
        default=UserStatus.ACTIVE
    )

    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
