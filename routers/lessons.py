"""One request for today's teaching cards, including substitutions and transfers."""
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from clock import today
from lesson_service import require_teaching, group_query, DAYS
import models

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])


@router.get("/today")
def today_lessons(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    require_teaching(user)
    on = today()
    subs = db.query(models.TeacherSubstitution).filter_by(date=on).all()
    sub_map = {s.group_id: s for s in subs}
    sub_ids = [s.group_id for s in subs if s.substitute_teacher_id == user.id]
    owned_report_groups = db.query(models.LessonReport.group_id).filter_by(date=on, teacher_id=user.id)
    groups = group_query(db).filter(or_(models.Group.teacher_id == user.id, models.Group.id.in_(sub_ids), models.Group.id.in_(owned_report_groups))).all()
    ids = [g.id for g in groups]
    reports = db.query(models.LessonReport).filter(models.LessonReport.group_id.in_(ids), models.LessonReport.date == on).all()
    report_map = {}
    for r in reports:
        report_map.setdefault(r.group_id, []).append(r)
    cancels = {c.group_id: c for c in db.query(models.CancelledLesson).filter(models.CancelledLesson.group_id.in_(ids), models.CancelledLesson.date == on).all()}
    transfers = db.query(models.TransferredLesson).filter(models.TransferredLesson.group_id.in_(ids), or_(models.TransferredLesson.date == on, models.TransferredLesson.new_date == on)).all()
    away = {t.group_id: t for t in transfers if t.date == on}
    incoming = {t.group_id: t for t in transfers if t.new_date == on}
    users = {u.id: u for u in db.query(models.User).filter(models.User.id.in_([s.substitute_teacher_id for s in subs])).all()}
    result = []
    for group in groups:
        known = report_map.get(group.id, [])
        sub = sub_map.get(group.id)
        assigned_id = sub.substitute_teacher_id if sub else group.teacher_id
        teacher = users.get(assigned_id) if sub else group.teacher
        day = DAYS[(incoming[group.id].date if group.id in incoming else on).weekday()]
        slots = [s for s in group.schedule_slots if s.day_of_week.value == day] if group.status == models.StatusEnum.ACTIVE else []
        legacy = next((r for r in known if r.slot_key == "legacy"), None)
        if legacy:
            pairs = [(None, legacy)]
        else:
            by_slot = {r.schedule_slot_id: r for r in known}
            pairs = [(s, by_slot.get(s.id)) for s in slots]
            ids_of_slots = {s.id for s in slots}
            pairs += [(None, r) for r in known if r.schedule_slot_id not in ids_of_slots]
        for slot, report in pairs:
            start = report.start_time if report else slot.start_time
            end = report.end_time if report else slot.end_time
            blocked = None
            if report:
                if report.teacher_id != user.id:
                    blocked = "Урок проведён другим преподавателем: " + (report.teacher_name or "неизвестно")
            elif slot and slot.end_time <= slot.start_time:
                blocked = "Некорректное время в старом расписании; обратитесь к администратору"
            elif group.id in cancels:
                blocked = "Урок отменён" + (": " + cancels[group.id].reason if cancels[group.id].reason else "")
            elif group.id in away:
                blocked = "Перенесён на " + away[group.id].new_date.strftime("%d.%m.%Y")
            elif assigned_id != user.id:
                blocked = "Заменяет: " + (teacher.full_name if teacher else "другой преподаватель")
            result.append({
                "group_id": group.id, "group_name": report.group_name if report else group.name,
                "subject": report.subject if report else group.subject,
                "classroom_name": group.classroom.name if group.classroom else None,
                "teacher_name": report.teacher_name if report else teacher.full_name if teacher else None,
                "slot_id": report.schedule_slot_id if report else slot.id,
                "report_id": report.id if report else None, "submitted": report is not None,
                "revision": report.revision if report else 0,
                "start_time": start.strftime("%H:%M") if start else None,
                "end_time": end.strftime("%H:%M") if end else None,
                "student_count": len(group.students), "blocked_reason": blocked,
                "can_open": not blocked, "needs_review": report.needs_review if report else False,
                "substitution": bool(sub and assigned_id == user.id),
                "transferred_from": str(incoming[group.id].date) if group.id in incoming else None,
            })
    result.sort(key=lambda row: (row["start_time"] or "00:00", row["group_name"], row["report_id"] or 0))
    return {"date": str(on), "lessons": result}
