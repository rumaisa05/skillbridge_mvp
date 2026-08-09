from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.challenge import Challenge
from ..models.submission import Submission
from ..models.notification import Notification
from ..schemas.challenge import ChallengeCreate, ChallengeOut
from ..security import get_current_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


def _sync_status(ch: Challenge) -> None:
    if ch.status == "open" and ch.deadline and ch.deadline <= datetime.utcnow():
        ch.status = "closed"


def _to_out(ch: Challenge) -> ChallengeOut:
    out = ChallengeOut.model_validate(ch)
    if ch.org:
        out.org_name = ch.org.name
    return out


@router.get("", response_model=list[ChallengeOut])
def list_challenges(
    search: str = Query("", description="Search by title or description"),
    category: str = Query("", description="Filter by category"),
    difficulty: str = Query("", description="Filter by difficulty"),
    status: str = Query("", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List challenges with optional search, filters, and pagination."""
    q = db.query(Challenge)
    for ch in q.all():
        _sync_status(ch)
    db.commit()

    if search:
        pattern = f"%{search}%"
        q = q.filter((Challenge.title.ilike(pattern)) | (Challenge.description.ilike(pattern)))
    if category:
        q = q.filter(Challenge.category == category)
    if difficulty:
        q = q.filter(Challenge.difficulty == difficulty)
    if status:
        q = q.filter(Challenge.status == status)

    q = q.order_by(Challenge.created_at.desc())
    total = q.count()

    offset = (page - 1) * limit
    items = q.offset(offset).limit(limit).all()

    return [_to_out(c) for c in items]


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    _sync_status(ch)
    db.commit()
    return _to_out(ch)


@router.post("", response_model=ChallengeOut)
def create_challenge(data: ChallengeCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    if current_user.role not in ("organization", "admin"):
        raise HTTPException(status_code=403, detail="Only organizations can create challenges")
    payload = data.model_dump()
    ch = Challenge(org_id=current_user.id, **payload)
    _sync_status(ch)
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return _to_out(ch)


@router.put("/{challenge_id}", response_model=ChallengeOut)
def update_challenge(challenge_id: int, data: ChallengeCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """Update a challenge (owner or admin only)."""
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.org_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the challenge owner can update this challenge")
    for field, value in data.model_dump().items():
        setattr(ch, field, value)
    _sync_status(ch)
    db.commit()
    db.refresh(ch)
    return _to_out(ch)


@router.delete("/{challenge_id}", response_model=dict)
def delete_challenge(challenge_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """Delete a challenge (owner or admin only)."""
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.org_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the challenge owner can delete this challenge")
    db.delete(ch)
    db.commit()
    return {"message": "Challenge deleted"}


@router.post("/{challenge_id}/select-winner", response_model=dict)
def select_winner(challenge_id: int, submission_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  feedback: str = Query("", description="Optional organizer feedback to attach to the winner portfolio entry")):
    """Organization selects a winning submission for their challenge."""
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.org_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the challenge owner can select a winner")

    sub = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.challenge_id == challenge_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found for this challenge")

    from ..models.portfolio import PortfolioEntry
    from ..models.report import AIReport
    import json

    portfolio = db.query(PortfolioEntry).filter(PortfolioEntry.submission_id == sub.id).first()
    if portfolio is None:
        report = db.query(AIReport).filter(AIReport.submission_id == sub.id).first()
        top_skills = []
        if report:
            scores = json.loads(report.dimension_scores or "{}")
            top_skills = sorted(scores, key=scores.get, reverse=True)[:3]
        portfolio = PortfolioEntry(
            participant_id=sub.participant_id,
            challenge_id=sub.challenge_id,
            submission_id=sub.id,
            title=ch.title,
            description=sub.description,
            skills_proven=json.dumps(top_skills),
            score=report.overall_score if report else 0,
            organization_feedback=feedback,
            is_winner=1,
        )
        db.add(portfolio)
    else:
        if feedback:
            portfolio.organization_feedback = feedback
        if portfolio.score == 0:
            report = db.query(AIReport).filter(AIReport.submission_id == sub.id).first()
            if report:
                portfolio.score = report.overall_score

    # Reset any previous winner for this challenge
    db.query(Submission).filter(Submission.challenge_id == challenge_id).update({"is_winner": 0})
    db.query(PortfolioEntry).filter(
        PortfolioEntry.challenge_id == challenge_id,
        PortfolioEntry.submission_id != sub.id,
    ).update({"is_winner": 0})
    sub.is_winner = 1
    portfolio.is_winner = 1
    ch.status = "selected"

    db.add(Notification(
        user_id=sub.participant_id,
        title="Challenge winner selected",
        body=f"Congratulations! Your submission for '{ch.title}' was selected as the winner. {feedback or 'The organizer shared positive feedback.'}",
        type="success",
    ))
    db.commit()
    return {"message": "Winner selected", "submission_id": submission_id, "portfolio_entry_id": portfolio.id}
