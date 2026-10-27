from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.base import get_db
from app.models.models import Course
from app.schemas.schemas import CourseOut

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).options(joinedload(Course.topics)).all()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: str, db: Session = Depends(get_db)):
    return db.query(Course).options(joinedload(Course.topics)).filter(Course.id == course_id).first()
