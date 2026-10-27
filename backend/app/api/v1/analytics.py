from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import CompetencyScore, Student, Topic, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/student/skill-radar")
def skill_radar(course_id: str, db: Session = Depends(get_db),
                 user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    scores = (
        db.query(CompetencyScore)
        .join(Topic, Topic.id == CompetencyScore.topic_id)
        .filter(CompetencyScore.student_id == student.id, Topic.course_id == course_id)
        .all()
    )
    return [
        {"topic": db.query(Topic).get(s.topic_id).name, "score": round(s.score_pct * 100, 1)}
        for s in scores
    ]


@router.get("/teacher/class-heatmap")
def class_heatmap(course_id: str, db: Session = Depends(get_db),
                   user: User = Depends(require_role("teacher"))):
    """Aggregate weak-topic frequency across all students in a course."""
    scores = (
        db.query(CompetencyScore)
        .join(Topic, Topic.id == CompetencyScore.topic_id)
        .filter(Topic.course_id == course_id)
        .all()
    )
    topic_weak_counts = {}
    for s in scores:
        topic_name = db.query(Topic).get(s.topic_id).name
        topic_weak_counts.setdefault(topic_name, {"weak": 0, "average": 0, "strong": 0})
        topic_weak_counts[topic_name][s.level.value] += 1
    return topic_weak_counts


@router.get("/admin/institution-overview")
def institution_overview(db: Session = Depends(get_db),
                          user: User = Depends(require_role("admin"))):
    total_students = db.query(Student).count()
    avg_score = db.query(CompetencyScore).with_entities(CompetencyScore.score_pct).all()
    avg = round(sum(s[0] for s in avg_score) / len(avg_score) * 100, 1) if avg_score else 0
    return {"total_students": total_students, "average_competency_pct": avg}
