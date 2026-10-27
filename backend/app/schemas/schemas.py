from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class StudentRegister(BaseModel):
    email: EmailStr
    password: str
    reg_number: str
    semester: int
    department: str


class TeacherRegister(BaseModel):
    email: EmailStr
    password: str
    faculty_id: str
    assigned_courses: List[str] = []
    assigned_classes: List[str] = []


class AdminRegister(BaseModel):
    email: EmailStr
    password: str
    admin_id: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


# ---------- Courses ----------
class TopicOut(BaseModel):
    id: str
    name: str
    order_index: int

    class Config:
        from_attributes = True


class CourseOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    topics: List[TopicOut] = []

    class Config:
        from_attributes = True


# ---------- Questions / Quiz ----------
class QuestionOut(BaseModel):
    id: str
    topic_id: str
    difficulty: str
    question_text: str
    options: Dict[str, str]

    class Config:
        from_attributes = True


class DiagnosticStartOut(BaseModel):
    assessment_id: str
    questions: List[QuestionOut]


class QuizAnswerIn(BaseModel):
    question_id: str
    selected_option: str
    time_taken_sec: Optional[int] = None


class QuizSubmitIn(BaseModel):
    assessment_id: str
    answers: List[QuizAnswerIn]


# ---------- Competency ----------
class CompetencyTopicResult(BaseModel):
    topic_id: str
    topic_name: str
    score_pct: float
    level: str
    confidence_score: float
    estimated_hours: float
    reason_text: str


class CompetencyReport(BaseModel):
    course_id: str
    results: List[CompetencyTopicResult]


# ---------- Learning Path ----------
class DailyPlanItem(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    time_slot: str
    activity_type: str
    topic_id: Optional[str] = None
    topic_name: str
    completed: bool = False
    estimated_minutes: int = 30


class WeeklyPlanItem(BaseModel):
    id: Optional[str] = None
    day_of_week: str
    topic_id: Optional[str] = None
    topic_name: str
    activity_type: str


class LearningPathOut(BaseModel):
    id: Optional[str] = None
    course_id: str
    status: str = "active"
    wellness_adjustment: Optional[str] = None
    daily_plan: List[DailyPlanItem] = []
    weekly_plan: List[WeeklyPlanItem] = []


# ---------- Tutor ----------
class TutorChatIn(BaseModel):
    message: str
    course_id: Optional[str] = None
    language: str = "english"


class TutorChatOut(BaseModel):
    response: str
    sources: List[str] = []
    confidence: Optional[float] = 0.90
    grounded: Optional[bool] = True


# ---------- Materials ----------
class StudyMaterialOut(BaseModel):
    id: str
    topic_id: str
    topic_name: str
    type: str
    title: str
    url: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None


class MaterialFeedbackIn(BaseModel):
    material_id: str
    star_rating: int
    difficulty: int
    helpfulness: int
    comment: Optional[str] = None


# ---------- Gamification ----------
class BadgeOut(BaseModel):
    id: str
    badge_name: str
    earned_at: datetime
    description: Optional[str] = None
    icon: Optional[str] = None


class GamificationStatsOut(BaseModel):
    xp_points: int
    current_streak: int
    longest_streak: int
    rank: str
    next_rank_xp: int
    progress_pct: float
    badges: List[BadgeOut] = []


# ---------- Notifications ----------
class NotificationOut(BaseModel):
    id: str
    type: str
    message: str
    read_bool: bool
    created_at: datetime


# ---------- Wellness ----------
class WellnessCheckinIn(BaseModel):
    stress_level: int
    confidence_level: int
    sleep_quality: int
    workload: int
    motivation: int


# ---------- Career Stage Assessment ----------
class CareerAssessmentIn(BaseModel):
    resume_text: Optional[str] = None
    target_role: str
    job_description: Optional[str] = None


class ProgressionPlanOut(BaseModel):
    skills_to_learn: List[Dict[str, Any]] = []
    projects_to_build: List[Dict[str, Any]] = []
    assessments_to_take: List[Dict[str, Any]] = []
    study_materials_recommended: List[Dict[str, Any]] = []


class CareerAssessmentOut(BaseModel):
    id: str
    target_role: str
    career_stage: int
    stage_name: str
    readiness_score: float
    match_percentage: float
    stage_reason: str
    strengths: List[str] = []
    missing_skills: List[str] = []
    demonstrated_skills: List[str] = []
    score_breakdown: Dict[str, Any] = {}
    recommendations: List[str] = []
    progression_plan: Dict[str, Any] = {}
    extracted_skills: List[str] = []
    extracted_projects_count: int = 0
    extracted_experience_months: int = 0
    created_at: datetime


class TargetRoleOut(BaseModel):
    id: str
    name: str
    category: str
    description: str
    required_skills: List[str] = []
    recommended_projects: List[str] = []


