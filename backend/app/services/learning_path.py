from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.models import (
    LearningPath, DailyPlan, WeeklyPlan, CompetencyScore, 
    CompetencyLevelEnum, Topic, Student, MentalFeedback
)

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def generate_learning_path_for_student(db: Session, student_id: str, course_id: str) -> LearningPath:
    """
    Generates an adaptive Daily & Weekly learning path tailored to the student's
    competency gaps and current cognitive workload/wellness status.
    """
    # 1. Fetch student's competency scores for this course
    scores = (
        db.query(CompetencyScore)
        .join(Topic, Topic.id == CompetencyScore.topic_id)
        .filter(CompetencyScore.student_id == student_id, Topic.course_id == course_id)
        .all()
    )
    all_topics = db.query(Topic).filter(Topic.course_id == course_id).order_by(Topic.order_index).all()
    
    # 2. Fetch latest wellness check-in to adjust load
    latest_wellness = (
        db.query(MentalFeedback)
        .filter(MentalFeedback.student_id == student_id)
        .order_by(MentalFeedback.date.desc())
        .first()
    )
    is_high_stress = bool(latest_wellness and (latest_wellness.stress_level >= 7 or latest_wellness.workload >= 7))

    # Classify topics by priority
    weak_topics = [s.topic_id for s in scores if s.level == CompetencyLevelEnum.weak]
    avg_topics = [s.topic_id for s in scores if s.level == CompetencyLevelEnum.average]
    strong_topics = [s.topic_id for s in scores if s.level == CompetencyLevelEnum.strong]

    # If no scores exist yet, prioritize first topics
    if not weak_topics and not avg_topics and not strong_topics:
        ordered_ids = [t.id for t in all_topics]
    else:
        # Weak topics first, then average, then strong
        ordered_ids = weak_topics + avg_topics + [t.id for t in all_topics if t.id not in weak_topics and t.id not in avg_topics]

    if not ordered_ids and all_topics:
        ordered_ids = [t.id for t in all_topics]

    # Archive previous active paths
    db.query(LearningPath).filter(
        LearningPath.student_id == student_id,
        LearningPath.course_id == course_id,
        LearningPath.status == "active"
    ).update({"status": "archived"})

    # Create new active path
    new_path = LearningPath(
        student_id=student_id,
        course_id=course_id,
        generated_at=datetime.utcnow(),
        status="active"
    )
    db.add(new_path)
    db.flush()

    today = date.today()
    
    # Generate Daily Plan items
    time_slots_normal = [
        ("09:00 - 10:00", "Visual Concept Breakdown", 45),
        ("14:30 - 15:30", "Code Implementation & Cheatsheet", 45),
        ("18:30 - 19:15", "Adaptive Gap Practice Quiz", 30),
    ]
    time_slots_stressed = [
        ("10:00 - 10:30", "Light Concept Revision & Notes", 25),
        ("17:00 - 17:30", "Low-Stakes Micro Practice", 20),
    ]
    slots = time_slots_stressed if is_high_stress else time_slots_normal

    for idx, (slot, activity, duration) in enumerate(slots):
        topic_idx = idx % len(ordered_ids) if ordered_ids else 0
        assigned_topic_id = ordered_ids[topic_idx] if ordered_ids else (all_topics[0].id if all_topics else None)
        if assigned_topic_id:
            db.add(DailyPlan(
                learning_path_id=new_path.id,
                date=today,
                time_slot=slot,
                activity_type=activity,
                topic_id=assigned_topic_id,
                completed=False,
                estimated_minutes=duration
            ))

    # Generate Weekly Plan items across 7 days
    weekly_activities = [
        "Core Theory & Mental Model",
        "Video Walkthrough & Animation",
        "Hands-on Problem Solving",
        "Targeted Weak-Topic Remediation",
        "Cross-Topic Connection & Complexities",
        "Mastery Gate Readiness Assessment",
        "Weekly Recap & Peer Discussion"
    ]

    for day_idx, day_name in enumerate(DAYS_OF_WEEK):
        topic_idx = day_idx % len(ordered_ids) if ordered_ids else 0
        assigned_topic_id = ordered_ids[topic_idx] if ordered_ids else (all_topics[0].id if all_topics else None)
        activity = weekly_activities[day_idx]
        if is_high_stress and day_idx in (2, 6):
            activity = "Rest & Mental Wellness Reflection"

        if assigned_topic_id:
            db.add(WeeklyPlan(
                learning_path_id=new_path.id,
                day_of_week=day_name,
                topic_id=assigned_topic_id,
                activity_type=activity
            ))

    db.commit()
    db.refresh(new_path)
    return new_path
