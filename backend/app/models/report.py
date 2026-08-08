from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False, unique=True)
    overall_score = Column(Integer, default=0)
    dimension_scores = Column(Text, default="{}")  # JSON
    strengths = Column(Text, default="[]")  # JSON
    weaknesses = Column(Text, default="[]")  # JSON
    recommendations = Column(Text, default="[]")  # JSON
    model_used = Column(String, default="mock")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="report")
