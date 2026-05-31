from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from dependencies import get_current_user, require_admin
import models, schemas
from models import GroupStudent, ScheduleSlot, Attendance

router = APIRouter(prefix="/api/groups", tags=["Groups"])


def _build_group_out(g: models.Group) -> schemas.GroupOut:
    return schemas.GroupOut(
        id=g.id,
        name=g.name,
        grade=g.grade,
        language=g.language,
        teacher_id=g.teacher_id,
        classroom_id=g.classroom_id,
        capacity=g.capacity,
        branch=g.branch,
        status=g.status,
        created_at=g.created_at,
        student_count=len(g.students),
        teacher_name=g.teacher.full_name if g.teacher else None,
        classroom_name=g.classroom.name if g.classroom else None,
        schedule_slots=[schemas.ScheduleSlotOut.model_validate(s) for s in g.schedule_slots],
    )


@router.get("/", response_model=List[schemas.GroupOut])
def list_groups(
    grade: Optional[int] = Query(None),
    language: Optional[models.LangEnum] = Query(None),
    teacher_id: Optional[int] = Query(None),
    status: Optional[models.StatusEnum] = Query(None),
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Group)
    # Teachers only see their own groups
    if current_user.role == models.RoleEnum.teacher:
        q = q.filter(models.Group.teacher_id == current_user.id)
    else:
        if teacher_id:
            q = q.filter(models.Group.teacher_id == teacher_id)
    if grade is not None:
        q = q.filter(models.Group.grade == grade)
    if language:
        q = q.filter(models.Group.language == language)
    if status:
        q = q.filter(models.Group.status == status)
    if branch:
        q = q.filter(models.Group.branch == branch)
    groups = q.order_by(models.Group.grade, models.Group.name).all()
    return [_build_group_out(g) for g in groups]


@router.post("/", response_model=schemas.GroupOut, status_code=201)
def create_group(
    data: schemas.GroupCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    g = models.Group(**data.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return _build_group_out(g)


@router.get("/{group_id}", response_model=schemas.GroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return _build_group_out(g)


@router.put("/{group_id}", response_model=schemas.GroupOut)
def update_group(
    group_id: int,
    data: schemas.GroupUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(g, field, val)
    db.commit()
    db.refresh(g)
    return _build_group_out(g)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    db.query(models.GroupStudent).filter(
        models.GroupStudent.group_id == group_id).delete(synchronize_session=False)
    db.query(models.ScheduleSlot).filter(
        models.ScheduleSlot.group_id == group_id).delete(synchronize_session=False)
    db.query(models.Attendance).filter(
        models.Attendance.group_id == group_id).delete(synchronize_session=False)
    db.delete(g)
    db.commit()

# ── Students in group ──────────────────────────────────────────────────────────

@router.get("/{group_id}/students", response_model=List[schemas.StudentOut])
def list_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return [gs.student for gs in g.students]


@router.post("/{group_id}/students/{student_id}", status_code=201)
def add_student_to_group(
    group_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    exists = db.query(models.GroupStudent).filter_by(group_id=group_id, student_id=student_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Ученик уже в группе")
    db.add(models.GroupStudent(group_id=group_id, student_id=student_id))
    db.commit()
    return {"detail": "Ученик добавлен в группу"}


@router.delete("/{group_id}/students/{student_id}", status_code=204)
def remove_student_from_group(
    group_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    gs = db.query(models.GroupStudent).filter_by(group_id=group_id, student_id=student_id).first()
    if not gs:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(gs)
    db.commit()


# ── Schedule slots ─────────────────────────────────────────────────────────────

@router.post("/{group_id}/schedule", response_model=schemas.ScheduleSlotOut, status_code=201)
def add_schedule_slot(
    group_id: int,
    data: schemas.ScheduleSlotBase,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    slot = models.ScheduleSlot(group_id=group_id, **data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/schedule/{slot_id}", status_code=204)
def delete_schedule_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    slot = db.query(models.ScheduleSlot).filter(models.ScheduleSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Слот не найден")
    db.delete(slot)
    db.commit()
