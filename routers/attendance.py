from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date
from database import get_db
from dependencies import get_current_user
from clock import today
from lesson_service import (
    require_teaching, can_teach, group_query, date_slots, assigned_teacher_id,
    resolve_occurrence, report_metadata, assert_can_read_group, payroll, period,
)
import models, schemas

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


def _group(db, gid, lock=False):
    q = db.query(models.Group).filter_by(id=gid)
    if lock:
        q = q.with_for_update()
    group = q.first()
    if not group:
        raise HTTPException(404, "Группа не найдена")
    return group


def _frozen(db, on, ids=None):
    q = db.query(models.Freeze.student_id).filter(models.Freeze.start_date <= on, models.Freeze.end_date >= on)
    if ids is not None:
        q = q.filter(models.Freeze.student_id.in_(ids))
    return {row[0] for row in q.all()}


def _records(db, report):
    if not report:
        return []
    return db.query(models.Attendance).options(joinedload(models.Attendance.student)).filter_by(report_id=report.id).order_by(models.Attendance.student_id).all()


def _out(row, report):
    return schemas.AttendanceOut(
        id=row.id, report_id=row.report_id, group_id=row.group_id, student_id=row.student_id,
        student_name=row.student.full_name if row.student else "Удалённый ученик",
        date=row.date, status=row.status, score_1=row.score_1, score_2=row.score_2,
        lesson_topic=report.lesson_topic if report else row.lesson_topic,
        homework=report.homework if report else row.homework,
        recorded_by=row.recorded_by, teacher_id=report.teacher_id if report else None,
        revision=report.revision if report else None,
    )


@router.get("/context")
def attendance_context(group_id: int, on: date, slot_id: Optional[int] = None, report_id: Optional[int] = None,
                       db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    require_teaching(user)
    group = _group(db, group_id)
    report, slot, key = resolve_occurrence(db, group, on, slot_id, report_id)
    assert_can_read_group(db, group, user, on, report)
    records = _records(db, report)
    if report:
        students = {r.student.id: r.student for r in records if r.student}
    else:
        students = {s.id: s for s in db.query(models.Student).join(models.GroupStudent).filter(
            models.GroupStudent.group_id == group_id, models.Student.status == models.StatusEnum.ACTIVE,
        ).all()}
    may_edit = user.role == models.RoleEnum.admin or (
        report.teacher_id == user.id if report else assigned_teacher_id(db, group, on) == user.id and on == today()
    )
    return {
        "report": report_metadata(report), "can_edit": may_edit,
        "records": [_out(r, report) for r in records],
        "students": [schemas.StudentOut.model_validate(s) for s in sorted(students.values(), key=lambda s: s.full_name)],
        "frozen_ids": sorted({r.student_id for r in records if r.status == models.AttendanceStatus.none} if report else _frozen(db, on, list(students))),
    }


@router.post("/", status_code=201)
def save_attendance(data: schemas.AttendanceSaveRequest, db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    require_teaching(current_user)
    group = _group(db, data.group_id, lock=True)
    report, slot, key = resolve_occurrence(db, group, data.date, data.slot_id, data.report_id)
    is_admin = current_user.role == models.RoleEnum.admin
    if data.date > today():
        raise HTTPException(422, "Нельзя зафиксировать урок в будущем")
    if report:
        if not is_admin and report.teacher_id != current_user.id:
            raise HTTPException(403, "Этот урок провёл другой преподаватель; редактирование доступно администратору")
        if data.taught_by is not None and data.taught_by != report.teacher_id:
            raise HTTPException(409, "Автор проведённого урока не меняется при редактировании отчёта")
        if data.expected_revision != report.revision:
            raise HTTPException(409, "Отчёт уже изменён. Откройте его заново перед сохранением")
    else:
        if data.expected_revision != 0:
            raise HTTPException(409, "Исходный отчёт не найден; обновите страницу")
        if group.status != models.StatusEnum.ACTIVE:
            raise HTTPException(409, "Группа архивирована")
        if not is_admin and data.date != today():
            raise HTTPException(403, "Новый отчёт за прошлую дату оформляет администратор с указанием преподавателя")
        if data.taught_by is not None and not is_admin:
            raise HTTPException(403, "Нельзя назначать автора отчёта")
        if is_admin and data.date != today() and data.taught_by is None:
            raise HTTPException(422, "Для нового отчёта за прошлую дату явно укажите taught_by — фактического преподавателя")
        tid = data.taught_by if is_admin and data.taught_by is not None else assigned_teacher_id(db, group, data.date)
        teacher = db.get(models.User, tid) if tid else None
        if not teacher or not can_teach(teacher):
            raise HTTPException(422, "Назначьте группе преподавателя или преподавателя-администратора")
        if not is_admin and (tid != current_user.id or not teacher.is_active):
            raise HTTPException(403, "Этот урок ведёт другой преподаватель")
    if db.query(models.CancelledLesson.id).filter_by(group_id=group.id, date=data.date).first():
        raise HTTPException(409, "Урок отменён администратором")
    if db.query(models.TransferredLesson.id).filter_by(group_id=group.id, date=data.date).first():
        raise HTTPException(409, "Урок перенесён на другую дату")
    existing = _records(db, report)
    if report:
        expected_ids = {r.student_id for r in existing}
        if len(existing) != len(expected_ids):
            raise HTTPException(409, "В историческом отчёте найдены дубли; нужна отдельная сверка, исходные записи сохранены")
    else:
        expected_ids = {s[0] for s in db.query(models.Student.id).join(models.GroupStudent).filter(
            models.GroupStudent.group_id == group.id, models.Student.status == models.StatusEnum.ACTIVE,
        ).all()}
    supplied_ids = {r.student_id for r in data.records}
    if supplied_ids != expected_ids:
        raise HTTPException(409, "Состав учеников изменился или запрос содержит неполный/чужой список. Откройте отчёт заново")
    # A later freeze must not erase marks in an already submitted lesson.
    frozen = {r.student_id for r in existing if r.status == models.AttendanceStatus.none} if report else _frozen(db, data.date, supplied_ids)
    for rec in data.records:
        if rec.student_id not in frozen and rec.status == models.AttendanceStatus.none:
            raise HTTPException(422, "Отметьте присутствие или отсутствие каждого незамороженного ученика")
    try:
        if report:
            # Compare-and-swap works on SQLite too; never rely only on row locks.
            changed = db.query(models.LessonReport).filter_by(id=report.id, revision=data.expected_revision).update(
                {models.LessonReport.revision: data.expected_revision + 1,
                 models.LessonReport.lesson_topic: data.lesson_topic, models.LessonReport.homework: data.homework,
                 models.LessonReport.updated_by: current_user.id}, synchronize_session=False,
            )
            if changed != 1:
                db.rollback()
                raise HTTPException(409, "Другой пользователь уже изменил отчёт. Обновите его")
        else:
            report = models.LessonReport(
                group_id=group.id, date=data.date, slot_key=key, schedule_slot_id=slot.id,
                start_time=slot.start_time, end_time=slot.end_time, teacher_id=teacher.id,
                teacher_name=teacher.full_name, group_name=group.name, subject=group.subject,
                language=group.language.value if group.language else None, lesson_rate=teacher.hourly_rate,
                lesson_topic=data.lesson_topic, homework=data.homework, recorded_by=current_user.id,
                updated_by=current_user.id, revision=1, needs_review=False, provenance="submitted",
            )
            db.add(report)
            db.flush()
        existing_by_student = {row.student_id: row for row in existing}
        for rec in data.records:
            frozen_student = rec.student_id in frozen
            values = dict(
                status=models.AttendanceStatus.none if frozen_student else rec.status,
                score_1=None if frozen_student else rec.score_1,
                score_2=None if frozen_student else rec.score_2,
                lesson_topic=data.lesson_topic, homework=data.homework,
            )
            row = existing_by_student.get(rec.student_id)
            if row is not None:
                # Preserve attendance IDs, creation timestamps and legacy authors.
                for field, value in values.items():
                    setattr(row, field, value)
            else:
                db.add(models.Attendance(report_id=report.id, group_id=group.id,
                    student_id=rec.student_id, date=data.date,
                    recorded_by=report.recorded_by, **values))
        db.add(models.AuditLog(user_id=current_user.id, user_name=current_user.full_name,
                               action="update" if existing else "create", entity="attendance", entity_id=report.id,
                               summary=f"Отчёт #{report.id}, группа #{group.id}, {data.date}; преподаватель #{report.teacher_id}; {len(data.records)} учеников"))
        db.commit()
        db.refresh(report)
        return {"detail": f"Сохранено {len(data.records)} записей", "saved": len(data.records),
                "report_id": report.id, "revision": report.revision, "teacher_id": report.teacher_id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Этот урок уже сохранён другим запросом. Откройте отчёт заново")
    except Exception:
        db.rollback()
        raise


@router.get("/my-reports")
def my_reports(date_from: Optional[date] = None, date_to: Optional[date] = None, group_id: Optional[int] = None,
               db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    require_teaching(user)
    return payroll(db, date_from, date_to, teacher_id=user.id, group_id=group_id)[0]


@router.get("/frozen")
def frozen_students(on: date = Query(...), db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    require_teaching(user)
    return {"frozen_ids": sorted(_frozen(db, on))}


@router.get("/", response_model=List[schemas.AttendanceOut])
def get_attendance(group_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None,
                   report_id: Optional[int] = None, slot_id: Optional[int] = None,
                   db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    group = _group(db, group_id)
    assert_can_read_group(db, group, user)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "Неверный период")
    q = db.query(models.Attendance, models.LessonReport).join(models.LessonReport, models.Attendance.report_id == models.LessonReport.id).options(
        joinedload(models.Attendance.student),
    ).filter(models.Attendance.group_id == group_id)
    # Former teachers can still read their own historical reports, not another teacher's.
    if user.role != models.RoleEnum.admin and group.teacher_id != user.id:
        q = q.filter(models.LessonReport.teacher_id == user.id)
    if date_from:
        q = q.filter(models.Attendance.date >= date_from)
    if date_to:
        q = q.filter(models.Attendance.date <= date_to)
    if report_id:
        q = q.filter(models.LessonReport.id == report_id)
    if slot_id:
        q = q.filter(models.LessonReport.schedule_slot_id == slot_id)
    return [_out(row, report) for row, report in q.order_by(models.Attendance.date, models.Attendance.id).all()]


@router.get("/summary/{group_id}", response_model=List[schemas.AttendanceSummary])
def attendance_summary(group_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None,
                       db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    group = _group(db, group_id)
    assert_can_read_group(db, group, user)
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "Неверный период")
    students = db.query(models.Student).join(models.GroupStudent).filter(models.GroupStudent.group_id == group_id).all()
    q = db.query(models.Attendance).filter(models.Attendance.group_id == group_id)
    if date_from:
        q = q.filter(models.Attendance.date >= date_from)
    if date_to:
        q = q.filter(models.Attendance.date <= date_to)
    by_student = {}
    for r in q.all():
        by_student.setdefault(r.student_id, []).append(r)
    out = []
    for s in students:
        recs = by_student.get(s.id, [])
        marked = [r for r in recs if r.status != models.AttendanceStatus.none]
        present = sum(r.status == models.AttendanceStatus.present for r in marked)
        absent = sum(r.status == models.AttendanceStatus.absent for r in marked)
        scores = [x for r in recs for x in (r.score_1, r.score_2) if x is not None]
        out.append(schemas.AttendanceSummary(student_id=s.id, student_name=s.full_name,
            total_lessons=len(marked), present=present, absent=absent,
            attendance_rate=round(100 * present / len(marked), 1) if marked else 0,
            avg_score=round(sum(scores) / len(scores), 2) if scores else None))
    return out
