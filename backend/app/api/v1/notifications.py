from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import Notification, User
from app.schemas.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationOut])
def get_user_notifications(db: Session = Depends(get_db), user: User = Depends(require_role())):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )

    # If no notifications exist yet, create initial welcoming and onboarding notifications
    if not notifs:
        sample_notifs = [
            ("system", "Welcome to SkillPath AI! Complete your course diagnostic to identify skill gaps."),
            ("streak", "5-Day Learning Streak Active! Keep up the momentum to earn the Streak Master badge."),
            ("recommendation", "Weak topics detected in Trees and Graphs. Check your personalized daily plan for remedial practice."),
            ("mastery", "Arrays score reached 90%! Mastery Gate unlocked for advanced verification.")
        ]
        for n_type, msg in sample_notifs:
            n = Notification(user_id=user.id, type=n_type, message=msg, read_bool=False)
            db.add(n)
        db.commit()
        notifs = (
            db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    return notifs


@router.put("/{notif_id}/read")
def mark_notification_read(notif_id: str, db: Session = Depends(get_db), user: User = Depends(require_role())):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user.id).first()
    if notif:
        notif.read_bool = True
        db.commit()
    return {"status": "ok"}


@router.post("/mark-all-read")
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(require_role())):
    db.query(Notification).filter(Notification.user_id == user.id).update({"read_bool": True})
    db.commit()
    return {"status": "ok"}
