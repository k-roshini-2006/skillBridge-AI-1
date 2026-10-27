import enum
import uuid
from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Enum, Float,
                         ForeignKey, Integer, String, Text)
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)


class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    reg_number = Column(String, unique=True, nullable=False)
    semester = Column(Integer)
    department = Column(String)
    profile_pic_url = Column(String, nullable=True)
    xp_points = Column(Integer, default=0)

    user = relationship("User", back_populates="student")


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    faculty_id = Column(String, unique=True, nullable=False)
    assigned_courses = Column(JSON, default=list)
    assigned_classes = Column(JSON, default=list)

    user = relationship("User", back_populates="teacher")


class Admin(Base):
    __tablename__ = "admins"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    admin_id = Column(String, unique=True, nullable=False)

    user = relationship("User", back_populates="admin")


class Course(Base):
    __tablename__ = "courses"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    topics = relationship("Topic", back_populates="course")


class Topic(Base):
    __tablename__ = "topics"
    id = Column(String, primary_key=True, default=gen_uuid)
    course_id = Column(String, ForeignKey("courses.id"))
    name = Column(String, nullable=False)
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    materials = relationship("StudyMaterial", back_populates="topic")


class StudyMaterial(Base):
    __tablename__ = "study_materials"
    id = Column(String, primary_key=True, default=gen_uuid)
    topic_id = Column(String, ForeignKey("topics.id"))
    type = Column(String)  # notes|pdf|video|visualization|cheatsheet|interview_qs
    title = Column(String)
    url = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    source = Column(String, nullable=True)

    topic = relationship("Topic", back_populates="materials")


class DifficultyEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Question(Base):
    __tablename__ = "questions"
    id = Column(String, primary_key=True, default=gen_uuid)
    topic_id = Column(String, ForeignKey("topics.id"))
    difficulty = Column(Enum(DifficultyEnum), default=DifficultyEnum.medium)
    bloom_level = Column(String, nullable=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {"a": "...", "b": "...", ...}
    correct_answer = Column(String, nullable=False)  # key, e.g. "b"
    explanation = Column(Text, nullable=True)
    learning_objective = Column(Text, nullable=True)
    generated_for_student_id = Column(String, nullable=True)

    topic = relationship("Topic", back_populates="questions")


class AssessmentTypeEnum(str, enum.Enum):
    diagnostic = "diagnostic"
    weak_topic = "weak_topic"
    mastery = "mastery"


class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    course_id = Column(String, ForeignKey("courses.id"))
    type = Column(Enum(AssessmentTypeEnum), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=True)  # for weak/mastery
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    attempts = relationship("QuizAttempt", back_populates="assessment")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(String, primary_key=True, default=gen_uuid)
    assessment_id = Column(String, ForeignKey("assessments.id"))
    question_id = Column(String, ForeignKey("questions.id"))
    student_answer = Column(String, nullable=True)
    is_correct = Column(Boolean, default=False)
    time_taken_sec = Column(Integer, nullable=True)

    assessment = relationship("Assessment", back_populates="attempts")


class CompetencyLevelEnum(str, enum.Enum):
    strong = "strong"
    average = "average"
    weak = "weak"


class CompetencyScore(Base):
    __tablename__ = "competency_scores"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    topic_id = Column(String, ForeignKey("topics.id"))
    score_pct = Column(Float, default=0.0)
    level = Column(Enum(CompetencyLevelEnum), default=CompetencyLevelEnum.weak)
    confidence_score = Column(Float, default=0.0)
    estimated_hours = Column(Float, default=0.0)
    reason_text = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    course_id = Column(String, ForeignKey("courses.id"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")

    daily_plans = relationship("DailyPlan", cascade="all, delete-orphan")
    weekly_plans = relationship("WeeklyPlan", cascade="all, delete-orphan")


class DailyPlan(Base):
    __tablename__ = "daily_plan"
    id = Column(String, primary_key=True, default=gen_uuid)
    learning_path_id = Column(String, ForeignKey("learning_paths.id"))
    date = Column(Date, default=datetime.utcnow)
    time_slot = Column(String)
    activity_type = Column(String)
    topic_id = Column(String, ForeignKey("topics.id"))
    completed = Column(Boolean, default=False)
    estimated_minutes = Column(Integer, default=30)

    topic = relationship("Topic")


class WeeklyPlan(Base):
    __tablename__ = "weekly_plan"
    id = Column(String, primary_key=True, default=gen_uuid)
    learning_path_id = Column(String, ForeignKey("learning_paths.id"))
    day_of_week = Column(String)
    topic_id = Column(String, ForeignKey("topics.id"))
    activity_type = Column(String)

    topic = relationship("Topic")



class MentalFeedback(Base):
    __tablename__ = "mental_feedback"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, default=datetime.utcnow)
    stress_level = Column(Integer)
    confidence_level = Column(Integer)
    sleep_quality = Column(Integer)
    workload = Column(Integer)
    motivation = Column(Integer)


class MaterialFeedback(Base):
    __tablename__ = "material_feedback"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    material_id = Column(String, ForeignKey("study_materials.id"))
    star_rating = Column(Integer)
    difficulty = Column(Integer)
    helpfulness = Column(Integer)
    comment = Column(Text, nullable=True)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(String)
    message = Column(Text)
    read_bool = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Badge(Base):
    __tablename__ = "badges"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    badge_name = Column(String)
    earned_at = Column(DateTime, default=datetime.utcnow)


class Streak(Base):
    __tablename__ = "streaks"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    message = Column(Text)
    response = Column(Text)
    source_refs = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CareerAssessment(Base):
    __tablename__ = "career_assessments"
    id = Column(String, primary_key=True, default=gen_uuid)
    student_id = Column(String, ForeignKey("students.id"))
    target_role = Column(String, nullable=False)
    career_stage = Column(Integer, default=1)  # 1 to 5
    stage_name = Column(String, default="Beginner")
    readiness_score = Column(Float, default=0.0)  # 0 to 100
    match_percentage = Column(Float, default=0.0)  # 0 to 100
    stage_reason = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    demonstrated_skills = Column(JSON, default=list)
    score_breakdown = Column(JSON, default=dict)  # {skills, projects, experience, education}
    recommendations = Column(JSON, default=list)
    progression_plan = Column(JSON, default=dict)  # {skills_to_learn, projects_to_build, assessments_to_take}
    extracted_skills = Column(JSON, default=list)
    extracted_projects_count = Column(Integer, default=0)
    extracted_experience_months = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")

