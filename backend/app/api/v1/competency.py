from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import CompetencyScore, Student, Topic, User
from app.schemas.schemas import (CompetencyReport, CompetencyTopicResult,
                                  DiagnosticStartOut, QuestionOut, QuizSubmitIn)
from app.services.competency_engine import build_diagnostic_assessment, score_diagnostic

router = APIRouter(prefix="/competency", tags=["competency"])


def _student_id(db: Session, user: User) -> str:
    return db.query(Student).filter(Student.user_id == user.id).first().id


@router.post("/{course_id}/diagnostic/start", response_model=DiagnosticStartOut)
def start_diagnostic(course_id: str, db: Session = Depends(get_db),
                      user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    assessment = build_diagnostic_assessment(db, student_id, course_id)
    return DiagnosticStartOut(
        assessment_id=assessment.id,
        questions=assessment._question_pool,
    )


@router.post("/diagnostic/submit", response_model=CompetencyReport)
def submit_diagnostic(payload: QuizSubmitIn, db: Session = Depends(get_db),
                       user: User = Depends(require_role("student"))):
    answers = [a.dict() for a in payload.answers]
    results = score_diagnostic(db, payload.assessment_id, answers)
    course_id = db.query(Topic).filter(Topic.id == results[0]["topic_id"]).first().course_id if results else ""
    return CompetencyReport(
        course_id=course_id,
        results=[CompetencyTopicResult(**r) for r in results],
    )


@router.get("/{course_id}/report", response_model=CompetencyReport)
def get_report(course_id: str, db: Session = Depends(get_db),
                user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    scores = (
        db.query(CompetencyScore)
        .join(Topic, Topic.id == CompetencyScore.topic_id)
        .filter(CompetencyScore.student_id == student_id, Topic.course_id == course_id)
        .all()
    )
    results = [
        CompetencyTopicResult(
            topic_id=s.topic_id, topic_name=s.topic_id and db.query(Topic).get(s.topic_id).name,
            score_pct=round(s.score_pct * 100, 1), level=s.level.value,
            confidence_score=s.confidence_score, estimated_hours=s.estimated_hours,
            reason_text=s.reason_text or "",
        )
        for s in scores
    ]
    return CompetencyReport(course_id=course_id, results=results)
