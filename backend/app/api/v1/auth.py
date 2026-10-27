from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.base import get_db
from app.models.models import Admin, RoleEnum, Streak, Student, Teacher, User
from app.schemas.schemas import (AdminRegister, LoginRequest, StudentRegister,
                                  TeacherRegister, TokenResponse)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/student", response_model=TokenResponse)
def register_student(data: StudentRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role=RoleEnum.student)
    db.add(user)
    db.flush()
    student = Student(
        user_id=user.id,
        reg_number=data.reg_number,
        semester=data.semester,
        department=data.department,
    )
    db.add(student)
    db.flush()
    db.add(Streak(student_id=student.id, current_streak=0, longest_streak=0))
    db.commit()
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/register/teacher", response_model=TokenResponse)
def register_teacher(data: TeacherRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role=RoleEnum.teacher)
    db.add(user)
    db.flush()
    teacher = Teacher(
        user_id=user.id,
        faculty_id=data.faculty_id,
        assigned_courses=data.assigned_courses,
        assigned_classes=data.assigned_classes,
    )
    db.add(teacher)
    db.commit()
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/register/admin", response_model=TokenResponse)
def register_admin(data: AdminRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role=RoleEnum.admin)
    db.add(user)
    db.flush()
    db.add(Admin(user_id=user.id, admin_id=data.admin_id))
    db.commit()
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.role == data.role).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)
