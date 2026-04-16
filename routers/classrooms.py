from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from dependencies import get_current_user, require_admin
import models, schemas

router = APIRouter(prefix="/api/classrooms", tags=["Classrooms"])


@router.get("/", response_model=List[schemas.ClassroomOut])
def list_classrooms(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Classroom).order_by(models.Classroom.name).all()


@router.post("/", response_model=schemas.ClassroomOut, status_code=201)
def create_classroom(data: schemas.ClassroomCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    c = models.Classroom(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{classroom_id}", response_model=schemas.ClassroomOut)
def update_classroom(classroom_id: int, data: schemas.ClassroomUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    c = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Кабинет не найден")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(c, field, val)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{classroom_id}", status_code=204)
def delete_classroom(classroom_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    c = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Кабинет не найден")
    db.delete(c)
    db.commit()
