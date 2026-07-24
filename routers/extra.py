"""
Remaining routers: tasks, returns, enrollment forms,
ENT tests, forbidden dates, mentor assignments, analytics.
Each router is defined in this file and exported.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from database import get_db
from dependencies import get_current_user, require_admin, require_admin_or_manager, log_action
import models, schemas


# ══════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════
tasks_router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@tasks_router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    mine: bool = Query(False),
    status: Optional[models.TaskStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Task)
    if mine or current_user.role == models.RoleEnum.teacher:
        q = q.filter(models.Task.assigned_to == current_user.id)
    if status:
        q = q.filter(models.Task.status == status)
    tasks = q.order_by(models.Task.created_at.desc()).all()
    result = []
    for t in tasks:
        result.append(schemas.TaskOut(
            id=t.id,
            title=t.title,
            description=t.description,
            assigned_to=t.assigned_to,
            created_by=t.created_by,
            status=t.status,
            due_date=t.due_date,
            created_at=t.created_at,
            assignee_name=t.assignee.full_name if t.assignee else None,
            creator_name=t.creator.full_name if t.creator else None,
        ))
    return result


@tasks_router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task(
    data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = models.Task(**data.model_dump(), created_by=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return schemas.TaskOut(
        id=task.id, title=task.title, description=task.description,
        assigned_to=task.assigned_to, created_by=task.created_by,
        status=task.status, due_date=task.due_date, created_at=task.created_at,
        assignee_name=task.assignee.full_name if task.assignee else None,
        creator_name=current_user.full_name,
    )


@tasks_router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    # Only creator or admin can update
    if task.created_by != current_user.id and current_user.role != models.RoleEnum.admin:
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(task, field, val)
    db.commit()
    db.refresh(task)
    return schemas.TaskOut(
        id=task.id, title=task.title, description=task.description,
        assigned_to=task.assigned_to, created_by=task.created_by,
        status=task.status, due_date=task.due_date, created_at=task.created_at,
        assignee_name=task.assignee.full_name if task.assignee else None,
        creator_name=task.creator.full_name if task.creator else None,
    )


@tasks_router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()


# ══════════════════════════════════════════════════════
# RETURNS (Возвраты)
# ══════════════════════════════════════════════════════
returns_router = APIRouter(prefix="/api/returns", tags=["Returns"])


@returns_router.get("/", response_model=List[schemas.ReturnOut])
def list_returns(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Return).order_by(models.Return.created_at.desc()).offset(skip).limit(limit).all()


@returns_router.post("/", response_model=schemas.ReturnOut, status_code=201)
def create_return(
    data: schemas.ReturnCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    r = models.Return(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


# ══════════════════════════════════════════════════════
# ENROLLMENT FORMS (История форм)
# ══════════════════════════════════════════════════════
forms_router = APIRouter(prefix="/api/forms", tags=["Enrollment Forms"])


@forms_router.get("/", response_model=List[schemas.EnrollmentFormOut])
def list_forms(
    skip: int = 0, limit: int = 200,
    branch: Optional[str] = Query(None),
    language: Optional[models.LangEnum] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.EnrollmentForm)
    if branch:
        q = q.filter(models.EnrollmentForm.branch == branch)
    if language:
        q = q.filter(models.EnrollmentForm.language == language)
    forms = q.order_by(models.EnrollmentForm.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for f in forms:
        out = schemas.EnrollmentFormOut.model_validate(f)
        out.manager_name = f.manager.full_name if f.manager else None
        result.append(out)
    return result


@forms_router.post("/", response_model=schemas.EnrollmentFormOut, status_code=201)
def create_form(
    data: schemas.EnrollmentFormCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    f = models.EnrollmentForm(**data.model_dump(), manager_id=current_user.id)
    db.add(f)
    db.commit()
    db.refresh(f)
    out = schemas.EnrollmentFormOut.model_validate(f)
    out.manager_name = current_user.full_name
    return out


# ══════════════════════════════════════════════════════
# ENT TESTS
# ══════════════════════════════════════════════════════
ent_router = APIRouter(prefix="/api/ent", tags=["ENT Tests"])


@ent_router.get("/", response_model=List[schemas.ENTTestOut])
def list_ent(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.ENTTest).order_by(models.ENTTest.created_at.desc()).all()

@ent_router.get("/{test_id}")
def get_ent_one(test_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == test_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Тест не найден")
    return {
        "id": t.id,
        "name": t.name,
        "status": str(t.status.value) if hasattr(t.status, 'value') else str(t.status),
        "correct_answers": t.correct_answers or {},
    }


@ent_router.post("/", response_model=schemas.ENTTestOut, status_code=201)
def create_ent(data: schemas.ENTTestCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    t = models.ENTTest(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@ent_router.put("/{ent_id}", response_model=schemas.ENTTestOut)
def update_ent(ent_id: int, data: schemas.ENTTestUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == ent_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="ENT-тест не найден")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(t, field, val)
    db.commit()
    db.refresh(t)
    return t


@ent_router.delete("/{ent_id}", status_code=204)
def delete_ent(ent_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == ent_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="ENT-тест не найден")
    db.delete(t)
    db.commit()

@ent_router.get("/{test_id}/public")
def get_ent_public(test_id: int, db: Session = Depends(get_db)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == test_id).first()
    if not t:
        raise HTTPException(404, "Тест не найден")
    return {"id": t.id, "name": t.name, "status": t.status}

@ent_router.post("/{test_id}/submit")
def submit_ent(test_id: int, data: dict, db: Session = Depends(get_db)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == test_id).first()
    if not t:
        raise HTTPException(404, "Тест не найден")
    
    correct = t.correct_answers or {}
    student_answers = data.get("answers", {})
    subject1 = data.get("subject1", "")
    subject2 = data.get("subject2", "")
    scores = {}
    total = 0

    def calc_score(s_ans, c_ans_dict):
        score = 0
        for q_num, s_a in s_ans.items():
            c_a = c_ans_dict.get(str(q_num))
            if c_a is None:
                continue
    
            # Многовариантные вопросы (36-40) — список правильных
            if isinstance(c_a, list):
                if not isinstance(s_a, list):
                    s_a = [s_a]
                correct_set = set(c_a)
                selected_set = set(s_a)
                # Есть ли неверные ответы
                wrong = selected_set - correct_set
                if wrong:
                    # Если выбран хотя бы один неверный — 0 баллов
                    score += 0
                else:
                    correct_count = len(correct_set)
                    selected_count = len(selected_set & correct_set)
                    missing = correct_count - selected_count
                    if missing == 0:
                        # Все правильные выбраны: 3/3, 2/2, 1/1 → 2 балла
                        score += 2
                    elif missing == 1 and correct_count >= 2:
                        # Не хватает одного: 2/3, 1/2 → 1 балл
                        score += 1
                    else:
                        # 1/3, 0/anything → 0 баллов
                        score += 0
    
            # Одиночные вопросы (1-30, и части 31-35)
            else:
                if isinstance(s_a, str) and s_a == c_a:
                    score += 1
    
        return score

    # Base subjects
    for key in ['history', 'reading', 'math']:
        s_ans = student_answers.get(key, {})
        c_ans = correct.get(key, {})
        scores[key] = calc_score(s_ans, c_ans)
        total += scores[key]

    # Profile subjects - match by student's chosen subject name
    s1_ans = student_answers.get('subject1', {})
    c1_ans = correct.get(subject1, {})
    scores['subject1'] = calc_score(s1_ans, c1_ans)
    total += scores['subject1']

    s2_ans = student_answers.get('subject2', {})
    c2_ans = correct.get(subject2, {})
    scores['subject2'] = calc_score(s2_ans, c2_ans)
    total += scores['subject2']

    result = models.ENTStudentResult(
        test_id=test_id,
        student_name=data.get("student_name"),
        student_phone=data.get("student_phone"),
        grade=data.get("grade", 11),
        language=data.get("language", "RUS"),
        subject1=subject1,
        subject2=subject2,
        answers=student_answers,
        scores=scores,
        total_score=total,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {"scores": scores, "total": total, "id": result.id}
@ent_router.get("/{test_id}/results")
def get_ent_results(test_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    results = db.query(models.ENTStudentResult).filter(
        models.ENTStudentResult.test_id == test_id
    ).order_by(models.ENTStudentResult.created_at.desc()).all()
    return results

@ent_router.put("/{test_id}/answers")
def save_ent_answers(test_id: int, data: dict, db: Session = Depends(get_db), _=Depends(require_admin)):
    t = db.query(models.ENTTest).filter(models.ENTTest.id == test_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Тест не найден")
    t.correct_answers = data.get("answers", {})
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(t, "correct_answers")
    db.commit()
    db.refresh(t)
    return {"ok": True, "saved": t.correct_answers}

# ══════════════════════════════════════════════════════
# FORBIDDEN DATES (Запрещённые даты)
# ══════════════════════════════════════════════════════
forbidden_router = APIRouter(prefix="/api/forbidden-dates", tags=["Forbidden Dates"])


@forbidden_router.get("/", response_model=List[schemas.ForbiddenDateOut])
def list_forbidden(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.ForbiddenDate).order_by(models.ForbiddenDate.date).all()


@forbidden_router.post("/", response_model=schemas.ForbiddenDateOut, status_code=201)
def add_forbidden(
    data: schemas.ForbiddenDateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    if db.query(models.ForbiddenDate).filter(models.ForbiddenDate.date == data.date).first():
        raise HTTPException(status_code=400, detail="Эта дата уже добавлена")
    fd = models.ForbiddenDate(date=data.date, added_by=current_user.id)
    db.add(fd)
    db.commit()
    db.refresh(fd)
    return fd


@forbidden_router.delete("/{fd_id}", status_code=204)
def delete_forbidden(fd_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    fd = db.query(models.ForbiddenDate).filter(models.ForbiddenDate.id == fd_id).first()
    if not fd:
        raise HTTPException(status_code=404, detail="Дата не найдена")
    db.delete(fd)
    db.commit()


# ══════════════════════════════════════════════════════
# MENTOR ASSIGNMENTS
# ══════════════════════════════════════════════════════
mentors_router = APIRouter(prefix="/api/mentors", tags=["Mentor Assignments"])


@mentors_router.get("/assignments", response_model=List[schemas.MentorAssignOut])
def list_assignments(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    assignments = db.query(models.MentorAssignment).all()
    return [
        schemas.MentorAssignOut(
            id=a.id,
            mentor_id=a.mentor_id,
            mentor_name=a.mentor.full_name if a.mentor else "",
            student_id=a.student_id,
            student_name=a.student.full_name if a.student else "",
            assigned_at=a.assigned_at,
        ) for a in assignments
    ]


@mentors_router.post("/assignments", response_model=schemas.MentorAssignOut, status_code=201)
def assign_mentor(
    data: schemas.MentorAssignRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    mentor = db.query(models.User).filter(models.User.id == data.mentor_id, models.User.role == models.RoleEnum.mentor).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    student = db.query(models.Student).filter(models.Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    existing = db.query(models.MentorAssignment).filter_by(student_id=data.student_id).first()
    if existing:
        existing.mentor_id = data.mentor_id
        db.commit()
        db.refresh(existing)
        a = existing
    else:
        a = models.MentorAssignment(mentor_id=data.mentor_id, student_id=data.student_id)
        db.add(a)
        db.commit()
        db.refresh(a)
    return schemas.MentorAssignOut(
        id=a.id, mentor_id=a.mentor_id, mentor_name=mentor.full_name,
        student_id=a.student_id, student_name=student.full_name, assigned_at=a.assigned_at,
    )


@mentors_router.delete("/assignments/{assignment_id}", status_code=204)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    a = db.query(models.MentorAssignment).filter(models.MentorAssignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Назначение не найдено")
    db.delete(a)
    db.commit()


# ══════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════
analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@analytics_router.get("/summary", response_model=schemas.AnalyticsSummary)
def summary(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    total_students = db.query(models.Student).count()
    active_students = db.query(models.Student).filter(models.Student.status == models.StatusEnum.ACTIVE).count()
    total_groups = db.query(models.Group).count()
    active_groups = db.query(models.Group).filter(models.Group.status == models.StatusEnum.ACTIVE).count()
    total_teachers = db.query(models.User).filter(models.User.role == models.RoleEnum.teacher, models.User.is_active == True).count()
    total_mentors = db.query(models.User).filter(models.User.role == models.RoleEnum.mentor, models.User.is_active == True).count()
    total_managers = db.query(models.User).filter(models.User.role == models.RoleEnum.manager, models.User.is_active == True).count()
    return schemas.AnalyticsSummary(
        total_students=total_students,
        active_students=active_students,
        total_groups=total_groups,
        active_groups=active_groups,
        total_teachers=total_teachers,
        total_mentors=total_mentors,
        total_managers=total_managers,
    )


@analytics_router.get("/slots", response_model=List[schemas.SlotInfo])
def slots_info(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """Enrolled vs capacity per grade+language combo."""
    groups = db.query(models.Group).filter(models.Group.status == models.StatusEnum.ACTIVE).all()
    result = []
    for g in groups:
        enrolled = db.query(models.GroupStudent).filter_by(group_id=g.id).count()
        result.append(schemas.SlotInfo(
            grade=g.grade, language=g.language, enrolled=enrolled, capacity=g.capacity
        ))
    return result


@analytics_router.get("/group-size-distribution", response_model=List[schemas.GroupSizeDistribution])
def group_size_distribution(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    groups = db.query(models.Group).filter(models.Group.status == models.StatusEnum.ACTIVE).all()
    dist: dict[int, int] = {}
    for g in groups:
        size = db.query(models.GroupStudent).filter_by(group_id=g.id).count()
        dist[size] = dist.get(size, 0) + 1
    return [schemas.GroupSizeDistribution(size=k, count=v) for k, v in sorted(dist.items())]


@analytics_router.get("/overview")
def analytics_overview(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """Подробная аналитика: посещаемость, баллы, распределения, нагрузка."""
    from datetime import date, timedelta
    today = date.today()
    since = today - timedelta(days=30)

    # ── Посещаемость за 30 дней ──
    att = db.query(models.Attendance).filter(models.Attendance.date >= since).all()
    present = sum(1 for a in att if a.status == models.AttendanceStatus.present)
    absent = sum(1 for a in att if a.status == models.AttendanceStatus.absent)
    marked = present + absent
    attendance_rate = round(present / marked * 100, 1) if marked else 0.0

    # ── Средние баллы (по отметкам за 30 дней) ──
    s1 = [a.score_1 for a in att if a.score_1 is not None]
    s2 = [a.score_2 for a in att if a.score_2 is not None]
    avg_score_lesson = round(sum(s1) / len(s1), 2) if s1 else None
    avg_score_hw = round(sum(s2) / len(s2), 2) if s2 else None

    # ── Ученики по языкам ──
    students = db.query(models.Student).all()
    active_students = [s for s in students if s.status == models.StatusEnum.ACTIVE]
    by_lang: dict = {}
    for s in active_students:
        k = s.language.value if hasattr(s.language, "value") else str(s.language)
        by_lang[k] = by_lang.get(k, 0) + 1

    # ── Ученики по классам ──
    by_grade: dict = {}
    for s in active_students:
        by_grade[s.grade] = by_grade.get(s.grade, 0) + 1
    by_grade_list = [{"grade": k, "count": v} for k, v in sorted(by_grade.items())]

    # ── Группы по предметам ──
    groups = db.query(models.Group).filter(models.Group.status == models.StatusEnum.ACTIVE).all()
    by_subject: dict = {}
    for g in groups:
        subj = getattr(g, "subject", None) or "Без предмета"
        by_subject[subj] = by_subject.get(subj, 0) + 1
    by_subject_list = sorted(
        [{"subject": k, "count": v} for k, v in by_subject.items()],
        key=lambda x: -x["count"]
    )

    # ── Нагрузка преподавателей (групп на каждого) ──
    teachers = db.query(models.User).filter(
        models.User.role == models.RoleEnum.teacher, models.User.is_active == True).all()
    teacher_load = []
    for t in teachers:
        cnt = sum(1 for g in groups if g.teacher_id == t.id)
        teacher_load.append({"name": t.full_name, "groups": cnt})
    teacher_load.sort(key=lambda x: -x["groups"])

    # ── Заполняемость групп ──
    sizes = []
    for g in groups:
        sizes.append(db.query(models.GroupStudent).filter_by(group_id=g.id).count())
    avg_group_size = round(sum(sizes) / len(sizes), 1) if sizes else 0.0
    max_group_size = max(sizes) if sizes else 0
    min_group_size = min(sizes) if sizes else 0
    empty_groups = sum(1 for x in sizes if x == 0)

    # ── Активность за период ──
    cancelled_30 = db.query(models.CancelledLesson).filter(models.CancelledLesson.date >= since).count()
    freezes_active = db.query(models.Freeze).filter(
        models.Freeze.start_date <= today, models.Freeze.end_date >= today).count()
    lessons_recorded_30 = db.query(models.Attendance.group_id, models.Attendance.date).filter(
        models.Attendance.date >= since).distinct().count()

    return {
        "attendance": {
            "rate": attendance_rate, "present": present, "absent": absent,
            "marked": marked, "lessons_recorded": lessons_recorded_30,
        },
        "scores": {"avg_lesson": avg_score_lesson, "avg_hw": avg_score_hw},
        "by_language": by_lang,
        "by_grade": by_grade_list,
        "by_subject": by_subject_list,
        "teacher_load": teacher_load,
        "group_fill": {
            "avg": avg_group_size, "max": max_group_size,
            "min": min_group_size, "empty": empty_groups, "total": len(groups),
        },
        "activity": {"cancelled": cancelled_30, "freezes_active": freezes_active},
    }


@analytics_router.get("/teacher-reports")
def teacher_reports(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """Все отчёты всех преподавателей, сгруппированные по преподавателю. Со ставкой и суммой."""
    teachers = db.query(models.User).filter(models.User.role == models.RoleEnum.teacher).all()
    tinfo = {t.id: {"name": t.full_name, "rate": t.hourly_rate} for t in teachers}
    groups = db.query(models.Group).all()
    gname = {g.id: g.name for g in groups}
    glang = {g.id: (g.language.value if hasattr(g.language, "value") else str(g.language)) for g in groups}

    att = db.query(models.Attendance).all()
    # сгруппировать по (преподаватель -> группа+дата = урок)
    lessons = {}  # teacher_id -> { (group_id,date): {present,total,topic,homework} }
    for a in att:
        tid = a.recorded_by
        if tid is None:
            continue
        key = (a.group_id, a.date)
        lessons.setdefault(tid, {})
        L = lessons[tid].setdefault(key, {"present": 0, "total": 0, "topic": a.lesson_topic, "homework": a.homework})
        L["total"] += 1
        if a.status == models.AttendanceStatus.present:
            L["present"] += 1

    out = []
    for tid, lobj in lessons.items():
        info = tinfo.get(tid, {"name": "—", "rate": None})
        rate = info["rate"]
        reps = []
        for (gid, d), L in lobj.items():
            reps.append({
                "group": gname.get(gid, "—"),
                "language": glang.get(gid, ""),
                "date": str(d),
                "present": L["present"],
                "total": L["total"],
                "topic": L["topic"],
                "homework": L["homework"],
            })
        reps.sort(key=lambda r: r["date"], reverse=True)
        count = len(reps)
        out.append({
            "teacher_id": tid,
            "teacher_name": info["name"],
            "rate": rate,
            "lessons_count": count,
            "total_sum": (rate * count) if rate is not None else None,
            "reports": reps,
        })
    out.sort(key=lambda t: t["teacher_name"] or "")
    return out



# ══════════════════════════════════════════════════════
# FREEZES (Заморозки)
# ══════════════════════════════════════════════════════
freezes_router = APIRouter(prefix="/api/freezes", tags=["Freezes"])


@freezes_router.get("/", response_model=List[schemas.FreezeOut])
def list_freezes(
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Freeze)
    if student_id is not None:
        q = q.filter(models.Freeze.student_id == student_id)
    return q.order_by(models.Freeze.start_date.desc()).all()


@freezes_router.post("/", response_model=schemas.FreezeOut, status_code=201)
def create_freeze(
    data: schemas.FreezeCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    fr = models.Freeze(
        student_id=data.student_id,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason,
    )
    db.add(fr)
    db.commit()
    db.refresh(fr)
    log_action(db, _, "create", "freeze", fr.id, f"Заморозка ученика {student.full_name}: {fr.start_date}—{fr.end_date}")
    return fr


@freezes_router.delete("/{freeze_id}", status_code=204)
def delete_freeze(
    freeze_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    fr = db.query(models.Freeze).filter(models.Freeze.id == freeze_id).first()
    if fr:
        db.delete(fr)
        db.commit()
    return None


# ══════════════════════════════════════════════════════
# AUDIT LOG (Журнал действий) — только админ
# ══════════════════════════════════════════════════════
audit_router = APIRouter(prefix="/api/audit", tags=["Audit"])


@audit_router.get("/", response_model=List[schemas.AuditLogOut])
def list_audit(
    limit: int = Query(200, le=1000),
    entity: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    q = db.query(models.AuditLog)
    if entity:
        q = q.filter(models.AuditLog.entity == entity)
    if user_id is not None:
        q = q.filter(models.AuditLog.user_id == user_id)
    return q.order_by(models.AuditLog.created_at.desc()).limit(limit).all()


# ══════════════════════════════════════════════════════
# ХАРАКТЕРИСТИКИ (месячная обратная связь по ученикам)
# Пишут только преподаватели; читают преподаватели и админы.
# ══════════════════════════════════════════════════════
characteristics_router = APIRouter(prefix="/api/characteristics", tags=["Characteristics"])


@characteristics_router.get("/", response_model=List[schemas.CharacteristicOut])
def list_characteristics(
    student_id: Optional[int] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.Characteristic)
    if student_id is not None:
        q = q.filter(models.Characteristic.student_id == student_id)
    if period:
        q = q.filter(models.Characteristic.period == period)
    return q.order_by(models.Characteristic.period.desc(), models.Characteristic.id.desc()).all()


@characteristics_router.post("/", response_model=schemas.CharacteristicOut)
def upsert_characteristic(
    data: schemas.CharacteristicIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Только преподаватели могут писать/редактировать
    if current_user.role != models.RoleEnum.teacher:
        raise HTTPException(status_code=403, detail="Только преподаватель может писать характеристики")
    # Одна запись на (ученик, месяц, автор) — обновляем если уже есть
    existing = (
        db.query(models.Characteristic)
        .filter(
            models.Characteristic.student_id == data.student_id,
            models.Characteristic.period == data.period,
            models.Characteristic.author_id == current_user.id,
        )
        .first()
    )
    if existing:
        existing.text = data.text
        existing.author_name = current_user.full_name
        db.commit()
        db.refresh(existing)
        log_action(db, current_user, "update", "characteristic", existing.id, f"Характеристика ученика #{data.student_id} за {data.period}")
        return existing
    rec = models.Characteristic(
        student_id=data.student_id,
        author_id=current_user.id,
        author_name=current_user.full_name,
        period=data.period,
        text=data.text,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    log_action(db, current_user, "create", "characteristic", rec.id, f"Характеристика ученика #{data.student_id} за {data.period}")
    return rec


# ─── Cancelled Lessons (отмена урока админом) ───────────────────────────────
cancelled_router = APIRouter(prefix="/api/cancelled-lessons", tags=["Cancelled Lessons"])

@cancelled_router.get("/", response_model=List[schemas.CancelledLessonOut])
def list_cancelled(
    group_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.CancelledLesson)
    if group_id:
        q = q.filter(models.CancelledLesson.group_id == group_id)
    rows = q.order_by(models.CancelledLesson.date.desc()).all()
    out = []
    for r in rows:
        out.append(schemas.CancelledLessonOut(
            id=r.id, group_id=r.group_id, date=r.date, reason=r.reason,
            cancelled_by=r.cancelled_by,
            group_name=r.group.name if r.group else None,
            created_at=r.created_at,
        ))
    return out

@cancelled_router.post("/", response_model=schemas.CancelledLessonOut, status_code=201)
def cancel_lesson(
    data: schemas.CancelledLessonIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    group = db.query(models.Group).filter(models.Group.id == data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    # уже отменён на эту дату?
    existing = db.query(models.CancelledLesson).filter(
        models.CancelledLesson.group_id == data.group_id,
        models.CancelledLesson.date == data.date,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Урок на эту дату уже отменён")
    rec = models.CancelledLesson(
        group_id=data.group_id, date=data.date, reason=data.reason,
        cancelled_by=current_user.id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    log_action(db, current_user, "create", "cancelled_lesson", rec.id,
               f"Отменён урок группы {group.name} на {data.date}")
    return schemas.CancelledLessonOut(
        id=rec.id, group_id=rec.group_id, date=rec.date, reason=rec.reason,
        cancelled_by=rec.cancelled_by, group_name=group.name, created_at=rec.created_at,
    )

@cancelled_router.delete("/{cancel_id}", status_code=204)
def restore_lesson(
    cancel_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    rec = db.query(models.CancelledLesson).filter(models.CancelledLesson.id == cancel_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    gname = rec.group.name if rec.group else "?"
    gdate = rec.date
    db.delete(rec)
    db.commit()
    log_action(db, current_user, "delete", "cancelled_lesson", cancel_id,
               f"Восстановлен урок группы {gname} на {gdate}")


# ─── Transferred Lessons (админ переносит урок на другую дату) ─────────────
transfer_router = APIRouter(prefix="/api/transfer-lessons", tags=["Transferred Lessons"])

@transfer_router.get("/", response_model=List[schemas.TransferLessonOut])
def list_transferred(
    group_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.TransferredLesson)
    if group_id:
        q = q.filter(models.TransferredLesson.group_id == group_id)
    rows = q.order_by(models.TransferredLesson.date.desc()).all()
    out = []
    for r in rows:
        out.append(schemas.TransferLessonOut(
            id=r.id, group_id=r.group_id, date=r.date, new_date=r.new_date, reason=r.reason,
            transferred_by=r.transferred_by,
            group_name=r.group.name if r.group else None,
            created_at=r.created_at,
        ))
    return out

@transfer_router.post("/", response_model=schemas.TransferLessonOut, status_code=201)
def transfer_lesson(
    data: schemas.TransferLessonIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    group = db.query(models.Group).filter(models.Group.id == data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if data.new_date == data.date:
        raise HTTPException(status_code=400, detail="Новая дата совпадает с исходной")
    # уже перенесён с этой даты?
    existing = db.query(models.TransferredLesson).filter(
        models.TransferredLesson.group_id == data.group_id,
        models.TransferredLesson.date == data.date,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Урок на эту дату уже перенесён")
    rec = models.TransferredLesson(
        group_id=data.group_id, date=data.date, new_date=data.new_date, reason=data.reason,
        transferred_by=current_user.id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    log_action(db, current_user, "create", "transferred_lesson", rec.id,
               f"Перенесён урок группы {group.name} с {data.date} на {data.new_date}")
    return schemas.TransferLessonOut(
        id=rec.id, group_id=rec.group_id, date=rec.date, new_date=rec.new_date, reason=rec.reason,
        transferred_by=rec.transferred_by, group_name=group.name, created_at=rec.created_at,
    )

@transfer_router.delete("/{transfer_id}", status_code=204)
def cancel_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    rec = db.query(models.TransferredLesson).filter(models.TransferredLesson.id == transfer_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    gname = rec.group.name if rec.group else "?"
    gdate = rec.date
    db.delete(rec)
    db.commit()
    log_action(db, current_user, "delete", "transferred_lesson", transfer_id,
               f"Отменён перенос урока группы {gname} на {gdate}")


# ─── Fines (штрафы преподавателям) ──────────────────────────────────────────
fines_router = APIRouter(prefix="/api/fines", tags=["Fines"])

@fines_router.get("/", response_model=List[schemas.FineOut])
def list_fines(
    teacher_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Fine)
    if current_user.role == models.RoleEnum.teacher:
        # преподаватель видит только свои штрафы
        q = q.filter(models.Fine.teacher_id == current_user.id)
    elif teacher_id:
        q = q.filter(models.Fine.teacher_id == teacher_id)
    rows = q.order_by(models.Fine.created_at.desc()).all()
    out = []
    for r in rows:
        out.append(schemas.FineOut(
            id=r.id, teacher_id=r.teacher_id, amount=r.amount, reason=r.reason,
            issued_by=r.issued_by,
            teacher_name=r.teacher.full_name if r.teacher else None,
            created_at=r.created_at,
        ))
    return out

@fines_router.post("/", response_model=schemas.FineOut, status_code=201)
def create_fine(
    data: schemas.FineIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    teacher = db.query(models.User).filter(models.User.id == data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма штрафа должна быть больше нуля")
    rec = models.Fine(
        teacher_id=data.teacher_id, amount=data.amount, reason=data.reason,
        issued_by=current_user.id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    log_action(db, current_user, "create", "fine", rec.id,
               f"Штраф {data.amount} ₸ преподавателю {teacher.full_name}")
    return schemas.FineOut(
        id=rec.id, teacher_id=rec.teacher_id, amount=rec.amount, reason=rec.reason,
        issued_by=rec.issued_by, teacher_name=teacher.full_name, created_at=rec.created_at,
    )

@fines_router.delete("/{fine_id}", status_code=204)
def delete_fine(
    fine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    rec = db.query(models.Fine).filter(models.Fine.id == fine_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    tname = rec.teacher.full_name if rec.teacher else "?"
    amount = rec.amount
    db.delete(rec)
    db.commit()
    log_action(db, current_user, "delete", "fine", fine_id,
               f"Удалён штраф {amount} ₸ преподавателя {tname}")
