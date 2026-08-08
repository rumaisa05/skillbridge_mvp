from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repo_url = Column(String, default="")
    description = Column(Text, default="")
    docs_url = Column(String, default="")
    demo_url = Column(String, default="")
    status = Column(String, default="pending")  # pending/analyzing/analyzed/rejected
    is_winner = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="submissions")
    participant = relationship("User", backref="submissions")
    report = relationship("AIReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")
