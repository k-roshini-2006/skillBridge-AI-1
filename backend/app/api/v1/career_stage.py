from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import CareerAssessment, Student, User, Notification, Badge
from app.schemas.schemas import CareerAssessmentIn, CareerAssessmentOut, TargetRoleOut
from app.services.career_stage_engine import (
    TARGET_ROLES_DATABASE,
    assess_career_stage,
    extract_text_from_pdf,
)

router = APIRouter(prefix="/career-stage", tags=["career-stage"])


def _student_id(db: Session, user: User) -> str:
    st = db.query(Student).filter(Student.user_id == user.id).first()
    if not st:
        raise HTTPException(404, "Student profile not found")
    return st.id


@router.get("/target-roles", response_model=List[TargetRoleOut])
def get_target_roles():
    """Returns library of target job roles with required competencies and sample projects."""
    return [
        TargetRoleOut(
            id=role["id"],
            name=role["name"],
            category=role["category"],
            description=role["description"],
            required_skills=role["required_skills"],
            recommended_projects=role.get("recommended_projects", [])
        )
        for role in TARGET_ROLES_DATABASE.values()
    ]


@router.post("/assess-file", response_model=CareerAssessmentOut)
async def assess_resume_file(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student"))
):
    """
    Uploads a resume file (.pdf, .txt), parses technical evidence,
    and estimates the student's career readiness stage relative to target role.
    """
    student = db.query(Student).filter(Student.user_id == user.id).first()

    contents = await file.read()
    if file.filename.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(contents)
    else:
        try:
            resume_text = contents.decode("utf-8")
        except UnicodeDecodeError:
            resume_text = contents.decode("latin-1", errors="ignore")

    if not resume_text or len(resume_text.strip()) < 20:
        raise HTTPException(400, "Unable to extract readable text from uploaded resume. Please check the file or paste your resume text.")

    # Run Career Stage Assessment Engine
    assessment_data = assess_career_stage(
        resume_text=resume_text,
        target_role_id=target_role,
        custom_job_description=job_description
    )

    # Persist in DB
    record = CareerAssessment(
        student_id=student.id,
        target_role=assessment_data["target_role"],
        career_stage=assessment_data["career_stage"],
        stage_name=assessment_data["stage_name"],
        readiness_score=assessment_data["readiness_score"],
        match_percentage=assessment_data["match_percentage"],
        stage_reason=assessment_data["stage_reason"],
        strengths=assessment_data["strengths"],
        missing_skills=assessment_data["missing_skills"],
        demonstrated_skills=assessment_data["demonstrated_skills"],
        score_breakdown=assessment_data["score_breakdown"],
        recommendations=assessment_data["recommendations"],
        progression_plan=assessment_data["progression_plan"],
        extracted_skills=assessment_data["extracted_skills"],
        extracted_projects_count=assessment_data["extracted_projects_count"],
        extracted_experience_months=assessment_data["extracted_experience_months"],
    )
    db.add(record)

    # Award student +100 XP for career assessment
    student.xp_points = (student.xp_points or 0) + 100

    # Notification & Badge
    db.add(Notification(
        user_id=user.id,
        type="career_stage",
        message=f"🎯 Career Stage Assessed: You are estimated at Stage {assessment_data['career_stage']} ({assessment_data['stage_name']}) for {assessment_data['target_role']} with a readiness score of {assessment_data['readiness_score']}/100. (+100 XP awarded)"
    ))

    db.commit()
    db.refresh(record)

    return record


@router.post("/assess-text", response_model=CareerAssessmentOut)
def assess_resume_text(
    payload: CareerAssessmentIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student"))
):
    """Assesses career stage from pasted resume text."""
    student = db.query(Student).filter(Student.user_id == user.id).first()

    if not payload.resume_text or len(payload.resume_text.strip()) < 20:
        raise HTTPException(400, "Please provide sufficient resume text detailing your skills and projects.")

    assessment_data = assess_career_stage(
        resume_text=payload.resume_text,
        target_role_id=payload.target_role,
        custom_job_description=payload.job_description
    )

    record = CareerAssessment(
        student_id=student.id,
        target_role=assessment_data["target_role"],
        career_stage=assessment_data["career_stage"],
        stage_name=assessment_data["stage_name"],
        readiness_score=assessment_data["readiness_score"],
        match_percentage=assessment_data["match_percentage"],
        stage_reason=assessment_data["stage_reason"],
        strengths=assessment_data["strengths"],
        missing_skills=assessment_data["missing_skills"],
        demonstrated_skills=assessment_data["demonstrated_skills"],
        score_breakdown=assessment_data["score_breakdown"],
        recommendations=assessment_data["recommendations"],
        progression_plan=assessment_data["progression_plan"],
        extracted_skills=assessment_data["extracted_skills"],
        extracted_projects_count=assessment_data["extracted_projects_count"],
        extracted_experience_months=assessment_data["extracted_experience_months"],
    )
    db.add(record)

    student.xp_points = (student.xp_points or 0) + 100
    db.add(Notification(
        user_id=user.id,
        type="career_stage",
        message=f"🎯 Career Stage Assessed: Estimated at Stage {assessment_data['career_stage']} ({assessment_data['stage_name']}) for {assessment_data['target_role']} ({assessment_data['readiness_score']}/100)."
    ))

    db.commit()
    db.refresh(record)
    return record


@router.get("/latest", response_model=Optional[CareerAssessmentOut])
def get_latest_assessment(db: Session = Depends(get_db), user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    latest = (
        db.query(CareerAssessment)
        .filter(CareerAssessment.student_id == student.id)
        .order_by(CareerAssessment.created_at.desc())
        .first()
    )
    return latest


@router.get("/history", response_model=List[CareerAssessmentOut])
def get_assessment_history(db: Session = Depends(get_db), user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    records = (
        db.query(CareerAssessment)
        .filter(CareerAssessment.student_id == student.id)
        .order_by(CareerAssessment.created_at.desc())
        .limit(10)
        .all()
    )
    return records
