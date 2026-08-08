from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, default="web")  # web/mobile/ai/automation/data/design/other
    difficulty = Column(String, default="medium")  # easy/medium/hard
    reward = Column(String, default="")
    deadline = Column(DateTime, nullable=True)
    status = Column(String, default="open")  # open/closed/selected
    created_at = Column(DateTime, default=datetime.utcnow)

    org = relationship("User", backref="challenges")
    submissions = relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")
