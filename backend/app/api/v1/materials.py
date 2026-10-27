from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import StudyMaterial, MaterialFeedback, Student, User, Topic
from app.schemas.schemas import StudyMaterialOut, MaterialFeedbackIn

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/course/{course_id}", response_model=List[StudyMaterialOut])
def get_course_materials(course_id: str, topic_id: Optional[str] = None, material_type: Optional[str] = None,
                         db: Session = Depends(get_db)):
    query = db.query(StudyMaterial).join(Topic, Topic.id == StudyMaterial.topic_id).filter(Topic.course_id == course_id)
    if topic_id:
        query = query.filter(StudyMaterial.topic_id == topic_id)
    if material_type:
        query = query.filter(StudyMaterial.type == material_type)

    materials = query.all()
    return [
        StudyMaterialOut(
            id=m.id,
            topic_id=m.topic_id,
            topic_name=m.topic.name,
            type=m.type,
            title=m.title,
            url=m.url,
            content=m.content,
            source=m.source
        )
        for m in materials
    ]


@router.get("/topic/{topic_id}", response_model=List[StudyMaterialOut])
def get_topic_materials(topic_id: str, db: Session = Depends(get_db)):
    materials = db.query(StudyMaterial).filter(StudyMaterial.topic_id == topic_id).all()
    return [
        StudyMaterialOut(
            id=m.id,
            topic_id=m.topic_id,
            topic_name=m.topic.name if m.topic else "",
            type=m.type,
            title=m.title,
            url=m.url,
            content=m.content,
            source=m.source
        )
        for m in materials
    ]


@router.post("/{material_id}/feedback")
def submit_material_feedback(material_id: str, payload: MaterialFeedbackIn, db: Session = Depends(get_db),
                             user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(404, "Material not found")

    feedback = MaterialFeedback(
        student_id=student.id,
        material_id=material.id,
        star_rating=payload.star_rating,
        difficulty=payload.difficulty,
        helpfulness=payload.helpfulness,
        comment=payload.comment
    )
    db.add(feedback)
    
    # Award student +15 XP for rating study material
    student.xp_points = (student.xp_points or 0) + 15
    db.commit()

    return {"status": "success", "message": "Feedback submitted! +15 XP awarded."}
