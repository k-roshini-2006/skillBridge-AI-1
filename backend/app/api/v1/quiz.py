from datetime import datetime
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import (
    Assessment, QuizAttempt, Student, User, Question, Topic, CompetencyScore, 
    CompetencyLevelEnum, Notification, Badge
)
from app.schemas.schemas import QuizSubmitIn
from app.services.competency_engine import get_weak_topic_ids, classify_level
from app.services.quiz_generator import (
    build_mastery_assessment,
    build_weak_topic_assessment,
    evaluate_mastery
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _student_id(db: Session, user: User) -> str:
    st = db.query(Student).filter(Student.user_id == user.id).first()
    if not st:
        raise HTTPException(404, "Student profile not found")
    return st.id


@router.post("/{course_id}/weak-topics/start")
def start_weak_topic_quiz(course_id: str, db: Session = Depends(get_db),
                           user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    weak_topics = get_weak_topic_ids(db, student_id, course_id)
    if not weak_topics:
        # If no weak topics, pick topics that are not yet strong
        avg_scores = (
            db.query(CompetencyScore)
            .join(Topic, Topic.id == CompetencyScore.topic_id)
            .filter(CompetencyScore.student_id == student_id, Topic.course_id == course_id, CompetencyScore.level != CompetencyLevelEnum.strong)
            .all()
        )
        weak_topics = [s.topic_id for s in avg_scores]

    if not weak_topics:
        # Fall back to first 2 topics in the course for practice
        all_topics = db.query(Topic).filter(Topic.course_id == course_id).limit(2).all()
        weak_topics = [t.id for t in all_topics]

    if not weak_topics:
        raise HTTPException(400, "No topics available for practice quiz")

    result = build_weak_topic_assessment(db, student_id, course_id, weak_topics)
    return {
        "assessment_id": result["assessment_id"],
        "questions": [
            {
                "id": q.id,
                "topic_id": q.topic_id,
                "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                "question_text": q.question_text,
                "options": q.options,
                "bloom_level": q.bloom_level or "Understand"
            }
            for q in result["questions"]
        ],
    }


@router.post("/weak-topics/submit")
def submit_weak_topic_quiz(payload: QuizSubmitIn, db: Session = Depends(get_db),
                            user: User = Depends(require_role("student"))):
    assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not assessment:
        raise HTTPException(404, "Assessment not found")

    student = db.query(Student).filter(Student.id == assessment.student_id).first()
    assessment.submitted_at = datetime.utcnow()

    topic_stats = defaultdict(lambda: {"correct": 0, "total": 0, "name": ""})
    question_reviews = []

    for ans in payload.answers:
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        if not q:
            continue
        is_correct = bool(ans.selected_option == q.correct_answer)
        db.add(QuizAttempt(
            assessment_id=assessment.id,
            question_id=q.id,
            student_answer=ans.selected_option,
            is_correct=is_correct,
            time_taken_sec=ans.time_taken_sec or 15
        ))
        stats = topic_stats[q.topic_id]
        stats["total"] += 1
        stats["name"] = q.topic.name if q.topic else ""
        if is_correct:
            stats["correct"] += 1

        question_reviews.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "topic_name": q.topic.name if q.topic else "",
            "student_answer": ans.selected_option,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": q.explanation or "Direct concept definition and mechanics.",
            "learning_objective": q.learning_objective or "Understand core data structure behavior"
        })

    # Update competency scores for practiced topics
    topic_results = []
    for topic_id, stats in topic_stats.items():
        score_pct = stats["correct"] / stats["total"] if stats["total"] else 0.0
        new_level = classify_level(score_pct)

        score_rec = (
            db.query(CompetencyScore)
            .filter(CompetencyScore.student_id == student.id, CompetencyScore.topic_id == topic_id)
            .first()
        )
        if score_rec:
            # Weighted update with previous score
            score_rec.score_pct = round((score_rec.score_pct * 0.4) + (score_pct * 0.6), 2)
            score_rec.level = classify_level(score_rec.score_pct)
            score_rec.updated_at = datetime.utcnow()
            score_rec.reason_text = f"Practiced in Stage 2 weak-topic remediation. Recent accuracy: {round(score_pct * 100)}%."
        else:
            db.add(CompetencyScore(
                student_id=student.id,
                topic_id=topic_id,
                score_pct=score_pct,
                level=new_level,
                confidence_score=0.75,
                estimated_hours=1.5,
                reason_text=f"Initial practice assessment. Accuracy: {round(score_pct * 100)}%."
            ))

        topic_results.append({
            "topic_name": stats["name"],
            "accuracy_pct": round(score_pct * 100, 1),
            "level": new_level.value
        })

    # Award student +75 XP for completing weak-topic drill
    student.xp_points = (student.xp_points or 0) + 75
    db.commit()

    return {
        "assessment_id": assessment.id,
        "xp_awarded": 75,
        "total_xp": student.xp_points,
        "topic_results": topic_results,
        "questions": question_reviews,
        "message": "Weak-topic remediation drill completed! Competency profiles dynamically updated."
    }


@router.post("/topic/{topic_id}/mastery/start")
def start_mastery_quiz(topic_id: str, db: Session = Depends(get_db),
                        user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    result = build_mastery_assessment(db, student_id, topic_id, num_questions=8)
    topic = db.query(Topic).get(topic_id)
    return {
        "assessment_id": result["assessment_id"],
        "topic_name": topic.name if topic else "",
        "threshold": "80%",
        "questions": [
            {
                "id": q.id,
                "topic_id": q.topic_id,
                "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                "question_text": q.question_text,
                "options": q.options,
                "bloom_level": q.bloom_level or "Analyze"
            }
            for q in result["questions"]
        ],
    }


@router.post("/mastery/submit")
def submit_mastery_quiz(payload: QuizSubmitIn, db: Session = Depends(get_db),
                         user: User = Depends(require_role("student"))):
    assessment = db.query(Assessment).filter(Assessment.id == payload.assessment_id).first()
    if not assessment:
        raise HTTPException(404, "Assessment not found")

    student = db.query(Student).filter(Student.id == assessment.student_id).first()
    assessment.submitted_at = datetime.utcnow()

    correct = 0
    question_reviews = []
    for ans in payload.answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        is_correct = bool(question and ans.selected_option == question.correct_answer)
        if is_correct:
            correct += 1
        db.add(QuizAttempt(
            assessment_id=assessment.id,
            question_id=ans.question_id,
            student_answer=ans.selected_option,
            is_correct=is_correct,
            time_taken_sec=ans.time_taken_sec or 20,
        ))
        if question:
            question_reviews.append({
                "question_id": question.id,
                "question_text": question.question_text,
                "student_answer": ans.selected_option,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation or "Mastery verification criterion.",
                "learning_objective": question.learning_objective or "Rigorous algorithmic invariant analysis"
            })

    score_pct = correct / len(payload.answers) if payload.answers else 0.0
    passed = evaluate_mastery(score_pct)

    # If passed or improved, update topic CompetencyScore
    topic_name = "Topic"
    if assessment.topic_id:
        topic = db.query(Topic).get(assessment.topic_id)
        if topic:
            topic_name = topic.name

        score_rec = (
            db.query(CompetencyScore)
            .filter(CompetencyScore.student_id == student.id, CompetencyScore.topic_id == assessment.topic_id)
            .first()
        )
        if score_rec:
            score_rec.score_pct = max(score_rec.score_pct, score_pct)
            if passed:
                score_rec.level = CompetencyLevelEnum.strong
                score_rec.reason_text = f"Stage 3 Mastery Gate passed with {round(score_pct * 100)}%! Verified robust algorithmic comprehension."
            score_rec.updated_at = datetime.utcnow()
        elif passed:
            db.add(CompetencyScore(
                student_id=student.id,
                topic_id=assessment.topic_id,
                score_pct=score_pct,
                level=CompetencyLevelEnum.strong,
                confidence_score=0.95,
                estimated_hours=0.0,
                reason_text=f"Passed Stage 3 Mastery Gate at {round(score_pct * 100)}%."
            ))

    xp_awarded = 120 if passed else 40
    student.xp_points = (student.xp_points or 0) + xp_awarded

    if passed:
        # Notification and badge check
        db.add(Notification(
            user_id=student.user_id,
            type="mastery",
            message=f"🎉 Mastery Gate Passed! You scored {round(score_pct * 100)}% on {topic_name}. Next curriculum module unlocked!"
        ))
        # Award Mastery Gatekeeper badge
        has_badge = db.query(Badge).filter(Badge.student_id == student.id, Badge.badge_name == "Mastery Gatekeeper").first()
        if not has_badge:
            db.add(Badge(student_id=student.id, badge_name="Mastery Gatekeeper"))

    db.commit()

    return {
        "score_pct": round(score_pct * 100, 1),
        "passed": passed,
        "topic_unlocked_next": passed,
        "xp_awarded": xp_awarded,
        "total_xp": student.xp_points,
        "questions": question_reviews,
        "message": (
            f"🎉 Outstanding! Mastery achieved on {topic_name} ({round(score_pct * 100)}%). Next stage unlocked with +{xp_awarded} XP!"
            if passed else
            f"Scored {round(score_pct * 100)}% (threshold is 80%). Review recommended materials and attempt again with a fresh set."
        ),
    }


@router.get("/course/{course_id}/roadmap")
def get_course_roadmap(course_id: str, db: Session = Depends(get_db),
                       user: User = Depends(require_role("student"))):
    student_id = _student_id(db, user)
    topics = db.query(Topic).filter(Topic.course_id == course_id).order_by(Topic.order_index).all()
    scores = {
        s.topic_id: s
        for s in db.query(CompetencyScore).filter(CompetencyScore.student_id == student_id).all()
    }

    roadmap = []
    unlocked = True
    for idx, t in enumerate(topics):
        score_rec = scores.get(t.id)
        score_val = round(score_rec.score_pct * 100, 1) if score_rec else 0
        level = score_rec.level.value if score_rec else "unassessed"
        is_mastered = score_val >= 80

        roadmap.append({
            "topic_id": t.id,
            "topic_name": t.name,
            "order_index": t.order_index,
            "score_pct": score_val,
            "level": level,
            "is_mastered": is_mastered,
            "is_unlocked": unlocked,
            "questions_count": db.query(Question).filter(Question.topic_id == t.id).count(),
        })

        # Next topic is unlocked if current is mastered, or if first 2 topics
        if not is_mastered and idx >= 1:
            unlocked = False

    return roadmap
