import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.portfolio import PortfolioEntry
from ..schemas.portfolio import PortfolioOut
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/portfolio/mine", response_model=list[PortfolioOut])
def my_portfolio(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entries = db.query(PortfolioEntry).filter(PortfolioEntry.participant_id == current_user.id).all()
    result = []
    for e in entries:
        out = PortfolioOut.model_validate(e)
        if e.challenge:
            out.challenge_title = e.challenge.title
        if e.participant:
            out.participant_name = e.participant.name
        result.append(out)
    return result


@router.get("/portfolio/user/{user_id}", response_model=list[PortfolioOut])
def user_portfolio(user_id: int, db: Session = Depends(get_db)):
    entries = db.query(PortfolioEntry).filter(PortfolioEntry.participant_id == user_id).all()
    result = []
    for e in entries:
        out = PortfolioOut.model_validate(e)
        if e.challenge:
            out.challenge_title = e.challenge.title
        if e.participant:
            out.participant_name = e.participant.name
        result.append(out)
    return result


@router.get("/talent/search", response_model=list[dict])
def search_talent(
    q: str = Query("", description="Search by participant name or challenge title"),
    skills: str = Query("", description="Comma-separated skills to filter by"),
    skill: str = Query("", description="Single skill alias used by frontend or tests"),
    min_score: int = Query(0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """Search portfolios by name, skill, and minimum score for employers.

    Returns all matching portfolio entries regardless of winner status. Winning
    entries carry is_winner=1 so the frontend can badge them as organization-verified,
    while non-winning but AI-evaluated candidates are still surfaced.
    """
    query = db.query(PortfolioEntry).filter(
        PortfolioEntry.score >= min_score,
    )
    entries = query.order_by(PortfolioEntry.score.desc()).all()

    skill_filter = (skills or skill).strip()
    wanted_skills = [s.strip().lower() for s in skill_filter.split(",") if s.strip()] if skill_filter else []

    results = []
    for e in entries:
        participant = e.participant
        if q:
            needle = q.strip().lower()
            name_text = (participant.name if participant else "").lower()
            challenge_text = (e.challenge.title if e.challenge else "").lower()
            if needle not in name_text and needle not in challenge_text:
                continue

        skills_proven = []
        try:
            skills_proven = json.loads(e.skills_proven or "[]")
        except Exception:
            skills_proven = []

        if participant and participant.skills:
            try:
                user_skills = json.loads(participant.skills or "[]")
                for value in user_skills:
                    if value not in skills_proven:
                        skills_proven.append(value)
            except Exception:
                pass

        if wanted_skills and not any(skill in [str(x).lower() for x in skills_proven] for skill in wanted_skills):
            continue

        results.append({
            "id": e.id,
            "participant_id": e.participant_id,
            "participant_name": participant.name if participant else "Unknown",
            "participant_email": participant.email if participant else "",
            "participant_bio": participant.bio if participant else "",
            "participant_github": participant.github_url if participant else "",
            "title": e.title,
            "description": e.description,
            "skills_proven": [str(x) for x in skills_proven],
            "score": e.score,
            "challenge_title": e.challenge.title if e.challenge else "",
            "organization_feedback": e.organization_feedback or "",
            "is_winner": e.is_winner or 0,
            "created_at": str(e.created_at),
        })
    return results
