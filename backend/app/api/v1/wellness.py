from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import MentalFeedback, Student, User
from app.schemas.schemas import WellnessCheckinIn

router = APIRouter(prefix="/wellness", tags=["wellness"])


@router.post("/checkin")
def checkin(payload: WellnessCheckinIn, db: Session = Depends(get_db),
            user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    db.add(MentalFeedback(student_id=student.id, **payload.dict()))
    db.commit()

    adjust_workload = payload.stress_level >= 8 or payload.workload >= 8
    return {
        "recorded": True,
        "recommendation": (
            "High stress/workload detected — today's plan trimmed to revision + a short quiz."
            if adjust_workload else
            "Levels look manageable — continuing with the regular study plan."
        ),
    }
