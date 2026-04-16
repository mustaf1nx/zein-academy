from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from dependencies import get_current_user
import models, schemas

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/", status_code=201)
def save_attendance(
    data: schemas.AttendanceSaveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Save / overwrite attendance for a group on a specific date."""
    # Delete existing records for this group+date
    db.query(models.Attendance).filter(
        models.Attendance.group_id == data.group_id,
        models.Attendance.date == data.date,
    ).delete()

    for rec in data.records:
        att = models.Attendance(
            group_id=data.group_id,
            student_id=rec.student_id,
            date=data.date,
            status=rec.status,
            score_1=rec.score_1,
            score_2=rec.score_2,
            recorded_by=current_user.id,
        )
        db.add(att)
    db.commit()
    return {"detail": f"Сохранено {len(data.records)} записей"}


@router.get("/", response_model=List[schemas.AttendanceOut])
def get_attendance(
    group_id: int = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Attendance).filter(models.Attendance.group_id == group_id)
    if date_from:
        q = q.filter(models.Attendance.date >= date_from)
    if date_to:
        q = q.filter(models.Attendance.date <= date_to)
    records = q.order_by(models.Attendance.date).all()

    result = []
    for r in records:
        result.append(schemas.AttendanceOut(
            id=r.id,
            group_id=r.group_id,
            student_id=r.student_id,
            student_name=r.student.full_name if r.student else "",
            date=r.date,
            status=r.status,
            score_1=r.score_1,
            score_2=r.score_2,
        ))
    return result


@router.get("/summary/{group_id}", response_model=List[schemas.AttendanceSummary])
def attendance_summary(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Attendance statistics per student in a group."""
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    summaries = []
    for gs in group.students:
        student = gs.student
        q = db.query(models.Attendance).filter(
            models.Attendance.group_id == group_id,
            models.Attendance.student_id == student.id,
        )
        if date_from:
            q = q.filter(models.Attendance.date >= date_from)
        if date_to:
            q = q.filter(models.Attendance.date <= date_to)
        recs = q.all()
        total = len(recs)
        present = sum(1 for r in recs if r.status == models.AttendanceStatus.present)
        absent = sum(1 for r in recs if r.status == models.AttendanceStatus.absent)
        scores = [r.score_1 for r in recs if r.score_1 is not None] + \
                 [r.score_2 for r in recs if r.score_2 is not None]
        avg_score = round(sum(scores) / len(scores), 2) if scores else None

        summaries.append(schemas.AttendanceSummary(
            student_id=student.id,
            student_name=student.full_name,
            total_lessons=total,
            present=present,
            absent=absent,
            attendance_rate=round(present / total * 100, 1) if total else 0.0,
            avg_score=avg_score,
        ))
    return summaries
