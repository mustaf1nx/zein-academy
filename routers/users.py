from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from dependencies import get_current_user, require_admin, log_action
from auth import hash_password
import models, schemas

router = APIRouter(prefix="/api/users", tags=["Users / Staff"])


@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    role: Optional[models.RoleEnum] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    q = db.query(models.User)
    if role:
        q = q.filter(models.User.role == role)
    if is_active is not None:
        q = q.filter(models.User.is_active == is_active)
    return q.order_by(models.User.full_name).all()


@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(
    data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if db.query(models.User).filter(models.User.iin == data.iin).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким ИИН уже существует")
    user = models.User(
        iin=data.iin,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        initials=data.initials,
        role=data.role,
        phone=data.phone,
        subject=data.subject,
        hourly_rate=data.hourly_rate,
        branch=data.branch,
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось создать сотрудника. Проверьте, что ИИН уникален.")
    db.refresh(user)
    role_label = {"teacher":"преподаватель","mentor":"ментор","manager":"менеджер","lidoruby":"лидоруб","admin":"админ"}.get(getattr(user.role,'value',str(user.role)), getattr(user.role,'value',str(user.role)))
    log_action(db, current_user, "create", "user", user.id, f"Добавлен сотрудник: {user.full_name} ({role_label})")
    return user


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Own profile or admin
    if current_user.id != user_id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for field, val in data.model_dump(exclude_none=True).items():
        if field == "password":
            user.hashed_password = hash_password(val)
        else:
            setattr(user, field, val)
    db.commit()
    db.refresh(user)
    log_action(db, current_user, "update", "user", user.id, f"Изменён сотрудник: {user.full_name}")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Удалить/обнулить связанные данные, чтобы снять ссылки на пользователя
    db.query(models.MentorAssignment).filter(
        models.MentorAssignment.mentor_id == user_id).delete(synchronize_session=False)
    db.query(models.Task).filter(
        models.Task.assigned_to == user_id).delete(synchronize_session=False)
    db.query(models.Task).filter(
        models.Task.created_by == user_id).delete(synchronize_session=False)
    # Обнулить ссылки там, где поле допускает NULL (данные сохраняются)
    db.query(models.Group).filter(
        models.Group.teacher_id == user_id).update(
        {models.Group.teacher_id: None}, synchronize_session=False)
    db.query(models.Attendance).filter(
        models.Attendance.recorded_by == user_id).update(
        {models.Attendance.recorded_by: None}, synchronize_session=False)
    db.query(models.Student).filter(
        models.Student.manager_id == user_id).update(
        {models.Student.manager_id: None}, synchronize_session=False)
    db.query(models.Characteristic).filter(
        models.Characteristic.author_id == user_id).update(
        {models.Characteristic.author_id: None}, synchronize_session=False)
    db.query(models.AuditLog).filter(
        models.AuditLog.user_id == user_id).update(
        {models.AuditLog.user_id: None}, synchronize_session=False)
    uname = user.full_name
    db.delete(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось удалить сотрудника: есть связанные записи")
    log_action(db, current_user, "delete", "user", user_id, f"Удалён сотрудник: {uname}")