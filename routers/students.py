from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from dependencies import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("/", response_model=List[schemas.StudentOut])
def list_students(
    search: Optional[str] = Query(None),
    grade: Optional[int] = Query(None),
    language: Optional[models.LangEnum] = Query(None),
    status: Optional[models.StatusEnum] = Query(None),
    branch: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Student)
    if search:
        q = q.filter(models.Student.full_name.ilike(f"%{search}%"))
    if grade is not None:
        q = q.filter(models.Student.grade == grade)
    if language:
        q = q.filter(models.Student.language == language)
    if status:
        q = q.filter(models.Student.status == status)
    if branch:
        q = q.filter(models.Student.branch == branch)
    return q.order_by(models.Student.full_name).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.StudentOut, status_code=201)
def create_student(
    data: schemas.StudentCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    return s


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(s, field, val)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    # Удалить связанные данные
    db.query(models.GroupStudent).filter(
        models.GroupStudent.student_id == student_id).delete(synchronize_session=False)
    db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id).delete(synchronize_session=False)
    db.query(models.MentorAssignment).filter(
        models.MentorAssignment.student_id == student_id).delete(synchronize_session=False)
    db.query(models.Return).filter(
        models.Return.student_id == student_id).delete(synchronize_session=False)
    db.delete(s)
    db.commit()
