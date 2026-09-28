from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from lesson_service import can_teach
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
    if role == models.RoleEnum.teacher:
        q = q.filter(or_(models.User.role == role, and_(models.User.role == models.RoleEnum.admin, models.User.can_teach.is_(True))))
    elif role:
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
        can_teach=data.role == models.RoleEnum.teacher or (data.role == models.RoleEnum.admin and data.can_teach),
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
    changes = data.model_dump(exclude_unset=True)
    if current_user.role != models.RoleEnum.admin:
        forbidden = set(changes) - {"full_name", "initials", "phone", "password"}
        if forbidden:
            raise HTTPException(status_code=403, detail="Ставку, преподавательские права и статус меняет только администратор")
    if changes.get("can_teach") and user.role not in (models.RoleEnum.admin, models.RoleEnum.teacher):
        raise HTTPException(422, "Преподавательские права доступны только преподавателю или администратору")
    if user.id == current_user.id and changes.get("is_active") is False:
        raise HTTPException(400, "Нельзя деактивировать собственный аккаунт")
    if any(changes.get(k) is None for k in ("full_name", "is_active", "can_teach", "password") if k in changes):
        raise HTTPException(422, "Обязательное поле не может быть пустым")
    for field, val in changes.items():
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
    if user_id == current_user.id:
        raise HTTPException(400, "Нельзя деактивировать собственный аккаунт")
    # Never delete payroll provenance, fines, tasks or report authors.
    user.is_active = False
    db.commit()
    log_action(db, current_user, "update", "user", user_id, f"Архивирован сотрудник: {user.full_name}; история сохранена")
