"""Student-scoped, expiring freeze links. Knowing a numeric ID grants no access."""
from datetime import timedelta
from fastapi import HTTPException
from auth import create_access_token, decode_token
import models

LINK_DAYS = 30

def issue_freeze_token(student_id: int) -> str:
    return create_access_token({'sub':str(student_id),'purpose':'student_freeze'},timedelta(days=LINK_DAYS))

def verify_freeze_token(token: str | None, student_id: int) -> None:
    payload = decode_token(token) if token else None
    if not payload or payload.get('purpose') != 'student_freeze' or payload.get('sub') != str(student_id):
        raise HTTPException(403, 'Ссылка недействительна или истекла. Попросите у администратора новую ссылку заморозки')

def check_freeze_overlap(db, student_id, start, end):
    existing = db.query(models.Freeze.id).filter(models.Freeze.student_id==student_id,
        models.Freeze.start_date<=end, models.Freeze.end_date>=start).first()
    if existing:
        raise HTTPException(409,'На эти даты уже есть заморозка. Повторный период не добавлен')
