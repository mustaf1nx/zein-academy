from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import or_
from lesson_service import can_teach, group_query, assert_can_read_group
from typing import List, Optional
from database import get_db
from dependencies import get_current_user, require_admin, log_action
import models, schemas
from models import (
    GroupStudent, ScheduleSlot, Attendance,
    TeacherSubstitution, CancelledLesson, TransferredLesson,
)

router = APIRouter(prefix="/api/groups", tags=["Groups"])


def _build_group_out(g: models.Group) -> schemas.GroupOut:
    return schemas.GroupOut(
        id=g.id,
        name=g.name,
        subject=getattr(g, 'subject', None),
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
    mine: bool = Query(False),
    status: Optional[models.StatusEnum] = Query(None),
    branch: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = group_query(db)
    # Teachers only see their own groups
    if current_user.role == models.RoleEnum.teacher or mine:
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
    current_user: models.User = Depends(require_admin),
):
    payload = data.model_dump(exclude={"schedule", "student_ids"})
    _validate_references(db, payload)
    # Класс/язык убраны из UI, но в старой БД колонки могут быть NOT NULL — подставляем дефолты
    if payload.get("grade") is None:
        payload["grade"] = 0
    if payload.get("language") is None:
        payload["language"] = models.LangEnum.KAZ
    g = models.Group(**payload)
    db.add(g)
    db.flush()
    _replace_schedule_rows(db, g, data.schedule)
    ids = set(data.student_ids)
    valid_ids = {row[0] for row in db.query(models.Student.id).filter(
        models.Student.id.in_(ids), models.Student.status == models.StatusEnum.ACTIVE).all()}
    if ids != valid_ids or len(ids) != len(data.student_ids):
        raise HTTPException(422, "Выберите существующих активных учеников без повторений")
    for sid in ids:
        db.add(models.GroupStudent(group_id=g.id, student_id=sid))
    db.commit()
    db.refresh(g)
    log_action(db, current_user, "create", "group", g.id, f"Создана группа: {g.name}")
    return _build_group_out(g)


@router.get("/{group_id}", response_model=schemas.GroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if current_user.role == models.RoleEnum.teacher:
        assert_can_read_group(db, g, current_user)
    return _build_group_out(g)


@router.put("/{group_id}", response_model=schemas.GroupOut)
def update_group(
    group_id: int,
    data: schemas.GroupUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).with_for_update().first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    changes = data.model_dump(exclude_unset=True, exclude={"schedule"})
    _validate_references(db, changes)
    if any(changes.get(k) is None for k in ("name", "capacity", "status") if k in changes):
        raise HTTPException(422, "Обязательное поле не может быть пустым")
    for field, val in changes.items():
        setattr(g, field, val)
    if "schedule" in data.model_fields_set:
        if data.schedule is None:
            raise HTTPException(422, "Расписание должно быть списком")
        _replace_schedule_rows(db, g, data.schedule)
    elif "teacher_id" in changes or "classroom_id" in changes:
        _validate_slot_conflicts(db, g, g.schedule_slots, replace=True)
    db.commit()
    db.refresh(g)
    log_action(db, current_user, "update", "group", g.id, f"Изменена группа: {g.name}")
    return _build_group_out(g)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    g.status = models.StatusEnum.INACTIVE
    db.commit()
    log_action(db, current_user, "update", "group", group_id, f"Архивирована группа: {g.name}; журнал сохранён")

# ── Students in group ──────────────────────────────────────────────────────────

@router.get("/{group_id}/students", response_model=List[schemas.StudentOut])
def list_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    g = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if current_user.role == models.RoleEnum.teacher:
        assert_can_read_group(db, g, current_user)
    return db.query(models.Student).join(models.GroupStudent).filter(models.GroupStudent.group_id == group_id).order_by(models.Student.full_name).all()


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
    _validate_slots([data])
    _validate_slot_conflicts(db, g, [data], replace=False)
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


def _validate_references(db, payload):
    if payload.get("teacher_id") is not None:
        teacher = db.get(models.User, payload["teacher_id"])
        if not teacher or not teacher.is_active or not can_teach(teacher):
            raise HTTPException(422, "Выберите активного преподавателя или преподавателя-администратора")
    if payload.get("classroom_id") is not None:
        classroom = db.get(models.Classroom, payload["classroom_id"])
        if not classroom or not classroom.is_active:
            raise HTTPException(422, "Кабинет не найден или неактивен")


def _validate_slots(slots):
    for i, a in enumerate(slots):
        for b in slots[i+1:]:
            if a.day_of_week == b.day_of_week and a.start_time < b.end_time and b.start_time < a.end_time:
                raise HTTPException(409, "Слоты одной группы пересекаются")


def _validate_slot_conflicts(db, group, slots, replace):
    # Existing conflicts elsewhere are reported, never silently overwritten.
    related = db.query(models.ScheduleSlot, models.Group).join(models.Group).filter(models.Group.status == models.StatusEnum.ACTIVE).all()
    for new in slots:
        for old, other in related:
            if replace and other.id == group.id:
                continue
            common_resource = other.id == group.id or (group.teacher_id is not None and group.teacher_id == other.teacher_id) or (group.classroom_id is not None and group.classroom_id == other.classroom_id)
            if common_resource and new.day_of_week == old.day_of_week and new.start_time < old.end_time and old.start_time < new.end_time:
                raise HTTPException(409, f"Пересечение времени с группой «{other.name}»: преподаватель, кабинет или группа уже заняты")


@router.put("/{group_id}/schedule", response_model=List[schemas.ScheduleSlotOut])
def replace_schedule(group_id: int, data: List[schemas.ScheduleSlotBase], db: Session = Depends(get_db),
                     current_user: models.User = Depends(require_admin)):
    group = db.query(models.Group).filter_by(id=group_id).with_for_update().first()
    if not group:
        raise HTTPException(404, "Группа не найдена")
    _replace_schedule_rows(db, group, data)
    db.commit()
    log_action(db, current_user, "update", "schedule", group_id, f"Расписание группы «{group.name}» обновлено атомарно")
    return db.query(models.ScheduleSlot).filter_by(group_id=group_id).order_by(models.ScheduleSlot.day_of_week, models.ScheduleSlot.start_time).all()


def _replace_schedule_rows(db, group, data):
    _validate_slots(data)
    _validate_slot_conflicts(db, group, data, replace=True)
    # Retain unchanged IDs so a group edit does not create new lesson identities.
    existing = {(s.day_of_week, s.start_time, s.end_time): s for s in group.schedule_slots}
    wanted = {(s.day_of_week, s.start_time, s.end_time): s for s in data}
    for key, slot in existing.items():
        if key not in wanted:
            db.delete(slot)
    for key, item in wanted.items():
        if key not in existing:
            db.add(models.ScheduleSlot(group_id=group.id, **item.model_dump()))
