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
from dependencies import get_current_user, require_admin, require_admin_or_manager
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
        raise HTTPException(404)
    t.correct_answers = data.get("answers", {})
    db.commit()
    return {"ok": True}

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
