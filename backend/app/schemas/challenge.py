from pydantic import BaseModel
from datetime import datetime


class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: str = "web"
    difficulty: str = "medium"
    reward: str = ""
    deadline: datetime | None = None
    status: str = "open"


class ChallengeOut(BaseModel):
    id: int
    org_id: int
    title: str
    description: str
    category: str
    difficulty: str
    reward: str
    deadline: datetime | None = None
    status: str
    created_at: datetime
    org_name: str = ""

    class Config:
        from_attributes = True
