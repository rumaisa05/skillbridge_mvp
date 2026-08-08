from pydantic import BaseModel
from datetime import datetime


class PortfolioOut(BaseModel):
    id: int
    participant_id: int
    challenge_id: int
    submission_id: int
    title: str
    description: str
    skills_proven: str
    score: int
    organization_feedback: str
    created_at: datetime
    challenge_title: str = ""
    participant_name: str = ""

    class Config:
        from_attributes = True
