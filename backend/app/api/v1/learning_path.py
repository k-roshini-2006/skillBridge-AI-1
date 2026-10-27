from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import (
    LearningPath, DailyPlan, WeeklyPlan, Student, User, Topic, Course, MentalFeedback
)
from app.schemas.schemas import LearningPathOut, DailyPlanItem, WeeklyPlanItem
from app.services.learning_path import generate_learning_path_for_student

router = APIRouter(prefix="/learning-path", tags=["learning-path"])


def _student_id(db: Session, user: User) -> str:
    st = db.query(Student).filter(Student.user_id == user.id).first()
    if not st:
        raise HTTPException(404, "Student profile not found")
    return st.id


@router.get("", response_model=LearningPathOut)
def get_current_learning_path(course_id: Optional[str] = None, db: Session = Depends(get_db),
                              user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)

    # If course_id is not provided, pick the first enrolled course
    if not course_id:
        c = db.query(Course).first()
        course_id = c.id if c else ""

    path = (
        db.query(LearningPath)
        .filter(LearningPath.student_id == student_id, LearningPath.course_id == course_id, LearningPath.status == "active")
        .first()
    )

    if not path:
        path = generate_learning_path_for_student(db, student_id, course_id)

    # Check latest wellness for note
    latest_wellness = (
        db.query(MentalFeedback)
        .filter(MentalFeedback.student_id == student_id)
        .order_by(MentalFeedback.date.desc())
        .first()
    )
    adj_note = (
        "Adaptive workload adjustment active: Stress/Workload reduction applied to daily intervals."
        if latest_wellness and (latest_wellness.stress_level >= 7 or latest_wellness.workload >= 7)
        else "Standard pace calibrated for optimal retention."
    )

    daily_items = [
        DailyPlanItem(
            id=d.id,
            date=str(d.date) if d.date else "",
            time_slot=d.time_slot,
            activity_type=d.activity_type,
            topic_id=d.topic_id,
            topic_name=d.topic.name if d.topic else "General Review",
            completed=bool(d.completed),
            estimated_minutes=d.estimated_minutes or 30
        )
        for d in path.daily_plans
    ]

    weekly_items = [
        WeeklyPlanItem(
            id=w.id,
            day_of_week=w.day_of_week,
            topic_id=w.topic_id,
            topic_name=w.topic.name if w.topic else "General Review",
            activity_type=w.activity_type
        )
        for w in path.weekly_plans
    ]

    return LearningPathOut(
        id=path.id,
        course_id=path.course_id,
        status=path.status,
        wellness_adjustment=adj_note,
        daily_plan=daily_items,
        weekly_plan=weekly_items
    )


@router.post("/course/{course_id}/generate", response_model=LearningPathOut)
def regenerate_path(course_id: str, db: Session = Depends(get_db),
                     user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    generate_learning_path_for_student(db, student_id, course_id)
    return get_current_learning_path(course_id, db, user)


@router.put("/daily/{daily_id}/toggle-complete")
def toggle_daily_task(daily_id: str, db: Session = Depends(get_db),
                       user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    task = db.query(DailyPlan).filter(DailyPlan.id == daily_id).first()
    if not task:
        raise HTTPException(404, "Task not found")

    task.completed = not bool(task.completed)
    xp_change = 50 if task.completed else -50
    student.xp_points = max(0, (student.xp_points or 0) + xp_change)
    db.commit()

    return {
        "id": task.id,
        "completed": task.completed,
        "xp_awarded": xp_change,
        "total_xp": student.xp_points,
        "message": "Task completed! +50 XP awarded 🎯" if task.completed else "Task marked incomplete."
    }
