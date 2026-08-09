from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base
from enum import Enum


class UserRole(str, Enum):
    participant = "participant"
    organization = "organization"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default=UserRole.participant.value, nullable=False)
    bio = Column(Text, default="")
    skills = Column(Text, default="[]")  # JSON array string
    github_url = Column(String, default="")
    avatar_url = Column(String, default="")
    org_type = Column(String, default="")  # school | ngo | hospital | startup | company | other
    website = Column(String, default="")

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
