from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import Badge, Streak, Student, User, CompetencyScore, CompetencyLevelEnum, Assessment
from app.schemas.schemas import GamificationStatsOut, BadgeOut

router = APIRouter(prefix="/gamification", tags=["gamification"])

RANKS = [
    ("Bronze Scholar", 0, 500),
    ("Silver Practitioner", 500, 1000),
    ("Gold Strategist", 1000, 2000),
    ("Platinum Specialist", 2000, 3500),
    ("Diamond Architect", 3500, 5000),
]

BADGE_CATALOG = {
    "Diagnostic Pioneer": {
        "desc": "Completed your first comprehensive diagnostic assessment.",
        "icon": "compass"
    },
    "Mastery Gatekeeper": {
        "desc": "Passed a Stage 3 Mastery Gate with score ≥ 80%.",
        "icon": "shield-check"
    },
    "Streak Master": {
        "desc": "Maintained an active continuous study streak of 5+ days.",
        "icon": "flame"
    },
    "Array Ace": {
        "desc": "Achieved Strong mastery (≥ 80%) on Arrays and Memory Layouts.",
        "icon": "layers"
    },
    "Tree Titan": {
        "desc": "Achieved Strong mastery (≥ 80%) on Tree Traversals and BST.",
        "icon": "git-branch"
    },
    "Graph Gladiator": {
        "desc": "Achieved Strong mastery (≥ 80%) on Graph BFS/DFS Algorithms.",
        "icon": "share-2"
    },
    "Adaptive Explorer": {
        "desc": "Engaged with personalized daily learning activities and AI tutor.",
        "icon": "sparkles"
    }
}


def _check_and_award_badges(db: Session, student: Student):
    existing_badge_names = {b.badge_name for b in db.query(Badge).filter(Badge.student_id == student.id).all()}
    
    # 1. Diagnostic Pioneer check
    has_diagnostic = db.query(Assessment).filter(Assessment.student_id == student.id).first()
    if has_diagnostic and "Diagnostic Pioneer" not in existing_badge_names:
        db.add(Badge(student_id=student.id, badge_name="Diagnostic Pioneer"))
        existing_badge_names.add("Diagnostic Pioneer")

    # 2. Streak Master check
    streak = db.query(Streak).filter(Streak.student_id == student.id).first()
    if streak and streak.current_streak >= 5 and "Streak Master" not in existing_badge_names:
        db.add(Badge(student_id=student.id, badge_name="Streak Master"))
        existing_badge_names.add("Streak Master")

    # 3. Topic badges
    scores = db.query(CompetencyScore).filter(CompetencyScore.student_id == student.id).all()
    for s in scores:
        if s.score_pct >= 0.80:
            from app.models.models import Topic
            topic = db.query(Topic).get(s.topic_id)
            if topic:
                badge_key = None
                if "Array" in topic.name:
                    badge_key = "Array Ace"
                elif "Tree" in topic.name:
                    badge_key = "Tree Titan"
                elif "Graph" in topic.name:
                    badge_key = "Graph Gladiator"
                if badge_key and badge_key not in existing_badge_names:
                    db.add(Badge(student_id=student.id, badge_name=badge_key))
                    existing_badge_names.add(badge_key)

    # 4. Adaptive Explorer
    if (student.xp_points or 0) >= 500 and "Adaptive Explorer" not in existing_badge_names:
        db.add(Badge(student_id=student.id, badge_name="Adaptive Explorer"))
        existing_badge_names.add("Adaptive Explorer")

    db.commit()


@router.get("/stats", response_model=GamificationStatsOut)
def get_gamification_stats(db: Session = Depends(get_db),
                            user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    _check_and_award_badges(db, student)

    streak = db.query(Streak).filter(Streak.student_id == student.id).first()
    curr_streak = streak.current_streak if streak else 1
    long_streak = streak.longest_streak if streak else 1
    xp = student.xp_points or 0

    # Determine rank
    current_rank = "Bronze Scholar"
    next_xp = 500
    prev_xp = 0
    for r_name, min_x, max_x in RANKS:
        if xp >= min_x:
            current_rank = r_name
            prev_xp = min_x
            next_xp = max_x

    progress = min(100.0, max(0.0, round(((xp - prev_xp) / (next_xp - prev_xp)) * 100, 1)))

    badges = db.query(Badge).filter(Badge.student_id == student.id).order_by(Badge.earned_at.desc()).all()
    badge_outs = [
        BadgeOut(
            id=b.id,
            badge_name=b.badge_name,
            earned_at=b.earned_at,
            description=BADGE_CATALOG.get(b.badge_name, {}).get("desc", "Mastery milestone achieved."),
            icon=BADGE_CATALOG.get(b.badge_name, {}).get("icon", "award")
        )
        for b in badges
    ]

    return GamificationStatsOut(
        xp_points=xp,
        current_streak=curr_streak,
        longest_streak=long_streak,
        rank=current_rank,
        next_rank_xp=next_xp,
        progress_pct=progress,
        badges=badge_outs
    )


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.xp_points.desc()).limit(10).all()
    out = []
    for rank_idx, s in enumerate(students, 1):
        streak = db.query(Streak).filter(Streak.student_id == s.id).first()
        out.append({
            "rank": rank_idx,
            "reg_number": s.reg_number,
            "department": s.department or "Computer Science",
            "xp_points": s.xp_points or 0,
            "streak": streak.current_streak if streak else 0,
            "badges_count": db.query(Badge).filter(Badge.student_id == s.id).count()
        })
    return out
