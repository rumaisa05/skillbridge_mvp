from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.notification import Notification
from ..models.user import User
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/notifications", response_model=list[dict])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "title": item.title,
            "body": item.body,
            "type": item.type,
            "read": item.read,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]
