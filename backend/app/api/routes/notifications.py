from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Notification, Project, User
from app.services.presenters import build_user_map, serialize_notification


router = APIRouter()


@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = build_user_map(db)
    projects = {item.id: item for item in db.query(Project).all()}
    rows = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return [serialize_notification(item, users, projects) for item in rows]


@router.get("/notifications/unread-count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).count()  # noqa: E712
    return {"count": count}


@router.post("/notifications/{id}/read")
def mark_notification(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Notification).filter(Notification.id == id, Notification.user_id == current_user.id).first()
    if row:
        row.is_read = True
        row.read_at = datetime.utcnow()
        db.commit()
    return {"message": "已读"}


@router.post("/notifications/read")
def read_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).all()  # noqa: E712
    for row in rows:
        row.is_read = True
        row.read_at = datetime.utcnow()
    db.commit()
    return {"message": "已全部标记已读"}
