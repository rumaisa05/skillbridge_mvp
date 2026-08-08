from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    submission_id: int
    overall_score: int
    dimension_scores: str
    strengths: str
    weaknesses: str
    recommendations: str
    model_used: str
    summary: str

    class Config:
        from_attributes = True

