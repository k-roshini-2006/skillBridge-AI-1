import random
from collections import defaultdict
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import (Assessment, AssessmentTypeEnum,
                                CompetencyLevelEnum, CompetencyScore,
                                Question, QuizAttempt, Topic)


def build_diagnostic_assessment(db: Session, student_id: str, course_id: str,
                                 questions_per_topic: int = 5) -> Assessment:
    """Stage 1: mixed-topic diagnostic quiz, easy+medium, randomized order."""
    topics: List[Topic] = db.query(Topic).filter(Topic.course_id == course_id).all()

    assessment = Assessment(student_id=student_id, course_id=course_id,
                             type=AssessmentTypeEnum.diagnostic)
    db.add(assessment)
    db.flush()

    selected_questions = []
    for topic in topics:
        pool = (
            db.query(Question)
            .filter(Question.topic_id == topic.id, Question.difficulty.in_(["easy", "medium"]))
            .all()
        )
        random.shuffle(pool)
        selected_questions.extend(pool[:questions_per_topic])

    random.shuffle(selected_questions)
    db.commit()
    # Question order + assessment id returned to caller; attempts are created on submit.
    assessment._question_pool = selected_questions  # transient, not persisted
    return assessment


def classify_level(score_pct: float) -> CompetencyLevelEnum:
    if score_pct >= settings.STRONG_THRESHOLD:
        return CompetencyLevelEnum.strong
    if score_pct >= settings.WEAK_THRESHOLD:
        return CompetencyLevelEnum.average
    return CompetencyLevelEnum.weak


def estimate_hours(score_pct: float, num_questions_in_topic: int) -> float:
    """Simple heuristic: bigger gap + more content -> more estimated hours.
    Refine later using actual historical time-to-mastery data."""
    gap = max(0.0, 1.0 - score_pct)
    base_hours_per_topic = 2.0
    return round(base_hours_per_topic * gap * max(1, num_questions_in_topic / 5), 1)


def generate_reason_text(topic_name: str, score_pct: float, missed_objectives: List[str]) -> str:
    if not missed_objectives:
        objective_note = "a mix of concept and application questions."
    else:
        unique_objs = list(dict.fromkeys(missed_objectives))[:3]
        objective_note = "questions covering: " + "; ".join(unique_objs)
    pct = round(score_pct * 100)
    return (
        f"Scored {pct}% on {topic_name}. Missed {objective_note} "
        f"Recommend targeted review before attempting mastery quiz."
    )


def score_diagnostic(db: Session, assessment_id: str, answers: List[dict]) -> List[dict]:
    """
    answers: [{question_id, selected_option, time_taken_sec}]
    Persists QuizAttempt rows and CompetencyScore per topic, returns per-topic report.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    topic_stats = defaultdict(lambda: {"correct": 0, "total": 0, "missed_objectives": [], "name": ""})

    for ans in answers:
        question = db.query(Question).filter(Question.id == ans["question_id"]).first()
        if not question:
            continue
        is_correct = ans["selected_option"] == question.correct_answer
        attempt = QuizAttempt(
            assessment_id=assessment_id,
            question_id=question.id,
            student_answer=ans["selected_option"],
            is_correct=is_correct,
            time_taken_sec=ans.get("time_taken_sec"),
        )
        db.add(attempt)

        stats = topic_stats[question.topic_id]
        stats["total"] += 1
        stats["name"] = question.topic.name
        if is_correct:
            stats["correct"] += 1
        else:
            if question.learning_objective:
                stats["missed_objectives"].append(question.learning_objective)

    assessment.submitted_at = datetime.utcnow()

    results = []
    for topic_id, stats in topic_stats.items():
        score_pct = stats["correct"] / stats["total"] if stats["total"] else 0.0
        level = classify_level(score_pct)
        hours = estimate_hours(score_pct, stats["total"])
        reason = generate_reason_text(stats["name"], score_pct, stats["missed_objectives"])
        confidence = round(min(1.0, stats["total"] / 5), 2)  # more questions answered -> higher confidence

        existing = (
            db.query(CompetencyScore)
            .filter(CompetencyScore.student_id == assessment.student_id,
                    CompetencyScore.topic_id == topic_id)
            .first()
        )
        if existing:
            existing.score_pct = score_pct
            existing.level = level
            existing.confidence_score = confidence
            existing.estimated_hours = hours
            existing.reason_text = reason
        else:
            db.add(CompetencyScore(
                student_id=assessment.student_id, topic_id=topic_id,
                score_pct=score_pct, level=level, confidence_score=confidence,
                estimated_hours=hours, reason_text=reason,
            ))

        results.append({
            "topic_id": topic_id,
            "topic_name": stats["name"],
            "score_pct": round(score_pct * 100, 1),
            "level": level.value,
            "confidence_score": confidence,
            "estimated_hours": hours,
            "reason_text": reason,
        })

    db.commit()
    return results


def get_weak_topic_ids(db: Session, student_id: str, course_id: str) -> List[str]:
    scores = (
        db.query(CompetencyScore)
        .join(Topic, Topic.id == CompetencyScore.topic_id)
        .filter(CompetencyScore.student_id == student_id, Topic.course_id == course_id,
                CompetencyScore.level == CompetencyLevelEnum.weak)
        .all()
    )
    return [s.topic_id for s in scores]
