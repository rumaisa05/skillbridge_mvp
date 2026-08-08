from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.challenge import Challenge
from ..models.submission import Submission
from ..models.user import User
from ..security import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get("/summary")
def admin_summary(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    users = db.query(User).count()
    participants = db.query(User).filter(User.role == "participant").count()
    organizations = db.query(User).filter(User.role == "organization").count()
    challenges = db.query(Challenge).count()
    submissions = db.query(Submission).count()
    return {
        "users": users,
        "participants": participants,
        "organizations": organizations,
        "challenges": challenges,
        "submissions": submissions,
    }


@router.get("/users")
def admin_users(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    users = db.query(User).order_by(User.id.asc()).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "bio": user.bio,
            "skills": user.skills,
            "github_url": user.github_url,
            "avatar_url": user.avatar_url,
        }
        for user in users
    ]
