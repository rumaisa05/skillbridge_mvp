from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.challenge import Challenge
from ..models.notification import Notification
from ..models.portfolio import PortfolioEntry
from ..models.submission import Submission
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserOut, Token, Login, UserUpdate
from ..security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(func.lower(User.email) == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/auth/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/users/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/me", response_model=UserOut)
def update_me(data: UserUpdate, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    """Update the current user's profile."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/users/me")
def delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete the current user's account and related data."""
    db.query(Notification).filter(Notification.user_id == current_user.id).delete(synchronize_session=False)

    if current_user.role == UserRole.participant.value:
        db.query(PortfolioEntry).filter(PortfolioEntry.participant_id == current_user.id).delete(synchronize_session=False)
        submissions = db.query(Submission).filter(Submission.participant_id == current_user.id).all()
        for submission in submissions:
            db.delete(submission)

    if current_user.role == UserRole.organization.value:
        challenges = db.query(Challenge).filter(Challenge.org_id == current_user.id).all()
        challenge_ids = [challenge.id for challenge in challenges]
        if challenge_ids:
            db.query(PortfolioEntry).filter(PortfolioEntry.challenge_id.in_(challenge_ids)).delete(synchronize_session=False)
        for challenge in challenges:
            db.delete(challenge)

    db.delete(current_user)
    db.commit()
    return {"detail": "Account deleted"}
