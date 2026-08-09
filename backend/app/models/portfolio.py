from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class PortfolioEntry(Base):
    __tablename__ = "portfolio_entries"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    title = Column(String, default="")
    description = Column(Text, default="")
    skills_proven = Column(Text, default="[]")  # JSON
    score = Column(Integer, default=0)
    organization_feedback = Column(Text, default="")
    is_winner = Column(Integer, default=0)  # whether organization selected this as the winning submission
    created_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("User", backref="portfolio_entries")
    challenge = relationship("Challenge")
    submission = relationship("Submission")
