import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User, UserRole
from ..models.challenge import Challenge
from ..models.submission import Submission
from ..models.report import AIReport
from ..models.portfolio import PortfolioEntry
from ..models.notification import Notification
from ..schemas.submission import SubmissionCreate, SubmissionOut
from ..schemas.report import ReportOut
from ..ai.evaluator import evaluate_submission
from ..security import get_current_user

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


def _ensure_portfolio_entry(db: Session, submission_id: int, feedback: str = "") -> PortfolioEntry | None:
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        return None

    report = db.query(AIReport).filter(AIReport.submission_id == submission_id).first()
    if not report:
        return None

    def _extract_skills_from_text(*texts: str) -> list[str]:
        text = " ".join(t for t in texts if t).lower()
        tokens = [
            "python",
            "react",
            "javascript",
            "node",
            "django",
            "flask",
            "sql",
            "postgres",
            "postgresql",
            "typescript",
            "aws",
            "docker",
            "html",
            "css",
            "vue",
            "angular",
            "graphql",
            "fastapi",
        ]
        found: list[str] = []
        for tok in tokens:
            if tok in text and tok not in found:
                found.append(tok)
        return found

    top_skills = _extract_skills_from_text(sub.description or "", sub.challenge.description if sub.challenge else "", report.summary or "")

    participant_skills = []
    if sub.participant and sub.participant.skills:
        try:
            participant_skills = json.loads(sub.participant.skills or "[]")
        except Exception:
            participant_skills = []

    combined_skills = []
    for skill in [*top_skills, *participant_skills]:
        clean = str(skill).strip().lower().replace("_", " ")
        if clean and clean not in combined_skills:
            combined_skills.append(clean)

    entry = db.query(PortfolioEntry).filter(PortfolioEntry.submission_id == submission_id).first()

    if entry is None:
        entry = PortfolioEntry(
            participant_id=sub.participant_id,
            challenge_id=sub.challenge_id,
            submission_id=submission_id,
            title=sub.challenge.title if sub.challenge else "",
            description=sub.description,
            skills_proven=json.dumps(combined_skills),
            score=report.overall_score,
            organization_feedback=feedback,
        )
        db.add(entry)
    else:
        entry.title = sub.challenge.title if sub.challenge else entry.title
        entry.description = sub.description or entry.description
        entry.skills_proven = json.dumps(combined_skills)
        entry.score = report.overall_score
        if feedback:
            entry.organization_feedback = feedback
    db.commit()
    return entry


def _sub_out(s: Submission) -> SubmissionOut:
    out = SubmissionOut.model_validate(s)
    if s.participant:
        out.participant_name = s.participant.name
    return out


@router.get("", response_model=list[SubmissionOut])
def list_submissions(challenge_id: int | None = None, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    q = db.query(Submission)
    if challenge_id:
        q = q.filter(Submission.challenge_id == challenge_id)
    if current_user.role == "participant":
        q = q.filter(Submission.participant_id == current_user.id)
    elif current_user.role == "organization":
        # Organizations can only see submissions for their own challenges
        org_challenge_ids = [c.id for c in db.query(Challenge).filter(Challenge.org_id == current_user.id).all()]
        q = q.filter(Submission.challenge_id.in_(org_challenge_ids))
    return [_sub_out(s) for s in q.order_by(Submission.created_at.desc()).all()]


@router.post("", response_model=SubmissionOut)
def submit_solution(data: SubmissionCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    # Only participants (students/individuals) are allowed to submit solutions.
    if current_user.role != UserRole.participant.value:
        raise HTTPException(
            status_code=403,
            detail="Only participants (students/individuals) can submit solutions",
        )
    ch = db.query(Challenge).filter(Challenge.id == data.challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch.status != "open":
        raise HTTPException(status_code=400, detail="Challenge is closed")

    sub = Submission(participant_id=current_user.id, **data.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)

    # Immediately run AI evaluation (synchronous for prototype simplicity)
    sub.status = "analyzing"
    db.commit()
    result = evaluate_submission(description=data.description, repo_url=data.repo_url, category=ch.category)

    report = AIReport(
        submission_id=sub.id,
        overall_score=result.overall_score,
        dimension_scores=json.dumps(result.dimension_scores),
        strengths=json.dumps(result.strengths),
        weaknesses=json.dumps(result.weaknesses),
        recommendations=json.dumps(result.recommendations),
        model_used=result.model_used,
        summary=result.summary,
    )
    db.add(report)
    sub.status = "analyzed"
    db.commit()
    _ensure_portfolio_entry(db, sub.id)

    db.add(Notification(
        user_id=sub.participant_id,
        title="Submission evaluated",
        body=f"Your submission for '{sub.challenge.title if sub.challenge else 'this challenge'}' has been evaluated. View your AI report and portfolio entry.",
        type="info",
    ))
    db.commit()

    return _sub_out(sub)


@router.get("/{submission_id}/report", response_model=ReportOut)
def get_report(submission_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    is_owner_participant = sub.participant_id == current_user.id
    is_owner_org = sub.challenge is not None and sub.challenge.org_id == current_user.id
    if current_user.role != "admin" and not is_owner_participant and not is_owner_org:
        raise HTTPException(status_code=403, detail="You do not have access to this report")

    report = db.query(AIReport).filter(AIReport.submission_id == submission_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{submission_id}/portfolio", response_model=dict)
def create_portfolio_entry(submission_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user),
                           feedback: str = Query("", description="Optional feedback to attach to the portfolio entry")):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.participant_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only manage your own portfolio entries")

    entry = _ensure_portfolio_entry(db, submission_id, feedback=feedback)
    if entry is None:
        raise HTTPException(status_code=400, detail="No report yet")

    return {"message": "Portfolio entry created", "id": entry.id}
