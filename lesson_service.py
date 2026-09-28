"""Lesson identity, permissions, snapshots, and payroll queries."""
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import func, case, or_
from sqlalchemy.orm import joinedload, selectinload
import models
from clock import today, local_day, BUSINESS_TZ

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def can_teach(user):
    return user is not None and (user.role == models.RoleEnum.teacher or (
        user.role == models.RoleEnum.admin and user.can_teach
    ))


def require_teaching(user):
    if user.role != models.RoleEnum.admin and not can_teach(user):
        raise HTTPException(403, "Доступ только преподавателю или администратору")


def period(date_from=None, date_to=None):
    end = date_to or today()
    start = date_from or end.replace(day=1)
    if start > end:
        raise HTTPException(422, "Дата начала периода позже даты окончания")
    return start, end


def group_query(db):
    return db.query(models.Group).options(
        joinedload(models.Group.teacher), joinedload(models.Group.classroom),
        selectinload(models.Group.students), selectinload(models.Group.schedule_slots),
    )


def date_slots(db, group, on):
    """A transfer retains the source timetable's time slots."""
    incoming = db.query(models.TransferredLesson).filter_by(group_id=group.id, new_date=on).all()
    days = {DAYS[t.date.weekday()] for t in incoming} or {DAYS[on.weekday()]}
    return sorted((s for s in group.schedule_slots if s.day_of_week.value in days), key=lambda s: s.start_time)


def assigned_teacher_id(db, group, on):
    sub = db.query(models.TeacherSubstitution).filter_by(group_id=group.id, date=on).first()
    return sub.substitute_teacher_id if sub else group.teacher_id


def report_metadata(report):
    if not report:
        return None
    return {
        "id": report.id, "group_id": report.group_id, "date": str(report.date),
        "slot_id": report.schedule_slot_id, "revision": report.revision,
        "teacher_id": report.teacher_id, "teacher_name": report.teacher_name,
        "lesson_topic": report.lesson_topic, "homework": report.homework,
        "needs_review": report.needs_review, "review_note": report.review_note,
        "lesson_rate": report.lesson_rate, "provenance": report.provenance,
    }


def resolve_occurrence(db, group, on, slot_id=None, report_id=None):
    if report_id:
        report = db.get(models.LessonReport, report_id)
        if not report or report.group_id != group.id or report.date != on:
            raise HTTPException(404, "Отчёт не найден для этой группы и даты")
        if slot_id and report.schedule_slot_id and report.schedule_slot_id != slot_id:
            raise HTTPException(409, "Отчёт относится к другому времени урока")
        return report, None, report.slot_key
    # Old reports describe a whole group/day; never manufacture a second paid
    # lesson by matching those reports to a changed timetable.
    legacy = db.query(models.LessonReport).filter_by(group_id=group.id, date=on, slot_key="legacy").first()
    if legacy:
        return legacy, None, "legacy"
    slots = date_slots(db, group, on)
    if slot_id:
        slot = next((s for s in slots if s.id == slot_id), None)
        report = db.query(models.LessonReport).filter_by(group_id=group.id, date=on, slot_key=f"slot:{slot_id}").first()
        if report:
            return report, slot, report.slot_key
        if slot is None:
            raise HTTPException(422, "Этот слот не принадлежит уроку группы на выбранную дату")
    elif len(slots) == 1:
        slot = slots[0]
    elif len(slots) > 1:
        raise HTTPException(409, "На эту дату несколько уроков. Выберите конкретное время")
    else:
        raise HTTPException(422, "На эту дату нет урока по расписанию или переносу")
    if slot.end_time <= slot.start_time:
        raise HTTPException(422, "В старом расписании неверное время окончания. Администратор должен исправить слот")
    key = f"slot:{slot.id}"
    return db.query(models.LessonReport).filter_by(group_id=group.id, date=on, slot_key=key).first(), slot, key


def assert_can_read_group(db, group, user, on=None, report=None):
    if user.role == models.RoleEnum.admin:
        return
    require_teaching(user)
    if group.teacher_id == user.id or (report and report.teacher_id == user.id):
        return
    subs = db.query(models.TeacherSubstitution).filter_by(group_id=group.id, substitute_teacher_id=user.id)
    if on is not None:
        subs = subs.filter(models.TeacherSubstitution.date == on)
    if subs.first():
        return
    if on is None and report is None and db.query(models.LessonReport.id).filter_by(group_id=group.id, teacher_id=user.id).first():
        return
    raise HTTPException(403, "Нет доступа к журналу этой группы")


def payroll(db, date_from=None, date_to=None, teacher_id=None, group_id=None):
    """SQL aggregation instead of loading every student's all-time attendance."""
    start, end = period(date_from, date_to)
    counts = db.query(
        models.Attendance.report_id.label("rid"), func.count(models.Attendance.id).label("total"),
        func.sum(case((models.Attendance.status == models.AttendanceStatus.present, 1), else_=0)).label("present"),
    ).join(models.LessonReport, models.LessonReport.id == models.Attendance.report_id).filter(
        models.LessonReport.date >= start, models.LessonReport.date <= end,
    )
    if teacher_id is not None:
        counts = counts.filter(models.LessonReport.teacher_id == teacher_id)
    if group_id is not None:
        counts = counts.filter(models.LessonReport.group_id == group_id)
    counts = counts.group_by(models.Attendance.report_id).subquery()
    q = db.query(models.LessonReport, counts.c.total, counts.c.present).outerjoin(
        counts, counts.c.rid == models.LessonReport.id,
    ).filter(models.LessonReport.date >= start, models.LessonReport.date <= end)
    if teacher_id is not None:
        q = q.filter(models.LessonReport.teacher_id == teacher_id)
    if group_id is not None:
        q = q.filter(models.LessonReport.group_id == group_id)
    rows = q.order_by(models.LessonReport.date.desc(), models.LessonReport.start_time.desc()).all()
    # Timezone-aware [start, end+1) boundaries include the entire last day.
    lower = datetime.combine(start, time.min, BUSINESS_TZ).astimezone(timezone.utc)
    upper = datetime.combine(end + timedelta(days=1), time.min, BUSINESS_TZ).astimezone(timezone.utc)
    if db.bind.dialect.name == "sqlite":
        lower, upper = lower.replace(tzinfo=None), upper.replace(tzinfo=None)
    fq = db.query(models.Fine).filter(models.Fine.created_at >= lower, models.Fine.created_at < upper)
    if teacher_id is not None:
        fq = fq.filter(models.Fine.teacher_id == teacher_id)
    fines = fq.all()
    user_ids = {r.teacher_id for r, _, _ in rows if r.teacher_id is not None} | {f.teacher_id for f in fines}
    if teacher_id is not None:
        user_ids.add(teacher_id)
    users = {u.id: u for u in db.query(models.User).filter(models.User.id.in_(user_ids)).all()} if user_ids else {}
    buckets = {}

    def bucket(tid, historical_name=None):
        if tid not in buckets:
            user = users.get(tid)
            buckets[tid] = {
                "teacher_id": tid, "teacher_name": user.full_name if user else historical_name or "Неизвестный преподаватель",
                "is_active": user.is_active if user else False, "rate": user.hourly_rate if user else None,
                "date_from": str(start), "date_to": str(end), "reports": [], "fines": [],
                "lessons_count": 0, "gross_sum": 0, "fines_sum": 0, "total_sum": 0,
                "unpriced_lessons": 0, "needs_review_count": 0,
            }
        return buckets[tid]

    for report, total, present in rows:
        b = bucket(report.teacher_id, report.teacher_name)
        b["reports"].append({
            **report_metadata(report), "group": report.group_name, "subject": report.subject,
            "group_id": report.group_id, "language": report.language or "", "present": present or 0,
            "total": total or 0, "topic": report.lesson_topic, "homework": report.homework,
            "start_time": report.start_time.strftime("%H:%M") if report.start_time else None,
            "end_time": report.end_time.strftime("%H:%M") if report.end_time else None,
            "amount": report.lesson_rate,
        })
        b["lessons_count"] += 1
        if report.lesson_rate is None:
            b["unpriced_lessons"] += 1
        else:
            b["gross_sum"] += report.lesson_rate
        b["needs_review_count"] += int(report.needs_review)
    for fine in fines:
        b = bucket(fine.teacher_id)
        b["fines"].append({"id": fine.id, "teacher_id": fine.teacher_id, "amount": fine.amount,
                           "reason": fine.reason, "created_at": fine.created_at.isoformat(), "issued_on": str(local_day(fine.created_at))})
        b["fines_sum"] += fine.amount
    if teacher_id is not None:
        bucket(teacher_id)
    for b in buckets.values():
        b["known_total_sum"] = b["gross_sum"] - b["fines_sum"]
        b["total_sum"] = None if b["unpriced_lessons"] or b["needs_review_count"] else b["known_total_sum"]
    return sorted(buckets.values(), key=lambda b: b["teacher_name"].casefold())
