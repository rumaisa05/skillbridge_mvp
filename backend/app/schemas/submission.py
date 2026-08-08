from pydantic import BaseModel
from datetime import datetime


class SubmissionCreate(BaseModel):
    challenge_id: int
    repo_url: str = ""
    description: str = ""
    docs_url: str = ""
    demo_url: str = ""


class SubmissionOut(BaseModel):
    id: int
    challenge_id: int
    participant_id: int
    repo_url: str
    description: str
    docs_url: str
    demo_url: str
    status: str
    is_winner: int
    created_at: datetime
    participant_name: str = ""

    class Config:
        from_attributes = True

