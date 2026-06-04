"""
Zein Academy — Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
import models, os
import schemas
from auth import hash_password


from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.students import router as students_router
from routers.groups import router as groups_router
from routers.classrooms import router as classrooms_router
from routers.attendance import router as attendance_router
from routers.extra import (
    tasks_router, returns_router, forms_router, ent_router,
    forbidden_router, mentors_router, analytics_router, freezes_router, audit_router,
    characteristics_router,
)

models.Base.metadata.create_all(bind=engine)


# ── Лёгкая авто-миграция: добавляем недостающие колонки в существующие таблицы ──
def _ensure_columns():
    from sqlalchemy import inspect, text
    try:
        insp = inspect(engine)
        cols = [c["name"] for c in insp.get_columns("users")]
        if "hourly_rate" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN hourly_rate INTEGER"))
            print("✅ Миграция: добавлена колонка users.hourly_rate")
        # колонки темы урока и домашки в attendance
        try:
            acols = [c["name"] for c in insp.get_columns("attendance")]
            with engine.begin() as conn:
                if "lesson_topic" not in acols:
                    conn.execute(text("ALTER TABLE attendance ADD COLUMN lesson_topic TEXT"))
                    print("✅ Миграция: добавлена колонка attendance.lesson_topic")
                if "homework" not in acols:
                    conn.execute(text("ALTER TABLE attendance ADD COLUMN homework TEXT"))
                    print("✅ Миграция: добавлена колонка attendance.homework")
        except Exception as e:
            print(f"⚠ Миграция attendance пропущена: {e}")
        # колонка предмета у групп
        try:
            gcols = [c["name"] for c in insp.get_columns("groups")]
            if "subject" not in gcols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE groups ADD COLUMN subject VARCHAR(150)"))
                print("✅ Миграция: добавлена колонка groups.subject")
        except Exception as e:
            print(f"⚠ Миграция groups.subject пропущена: {e}")
    except Exception as e:
        print(f"⚠ Миграция hourly_rate пропущена: {e}")

_ensure_columns()

app = FastAPI(title="Zein Academy API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(students_router)
app.include_router(groups_router)
app.include_router(classrooms_router)
app.include_router(attendance_router)
app.include_router(tasks_router)
app.include_router(returns_router)
app.include_router(forms_router)
app.include_router(ent_router)
app.include_router(forbidden_router)
app.include_router(mentors_router)
app.include_router(analytics_router)
app.include_router(freezes_router)
app.include_router(audit_router)
app.include_router(characteristics_router)

# Статические файлы (логотипы и пр.)
_assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")


@app.on_event("startup")
def seed_default_admin():
    db = SessionLocal()
    try:
        # Главный аккаунт (твой) — не трогаем
        if not db.query(models.User).filter(models.User.iin == "900101350123").first():
            db.add(models.User(
                iin="900101350123",
                hashed_password=hash_password("zein2024"),
                full_name="Администратор",
                initials="АД",
                role=models.RoleEnum.admin,
                is_active=True,
            ))
            db.commit()
            print("✅ Admin создан: ИИН=900101350123 пароль=zein2024")
        else:
            print("ℹ Admin уже существует — seed пропущен")

        # ── 3 дополнительных админских аккаунта ──
        # Формат: ("ИИН", "пароль", "Фамилия Имя", "инициалы")
        extra_admins = [
            ("555555555555", "zein4821", "Бекенов Берикбек", "ББ"),
            ("666666666666", "zein7263", "Айдынұлы Әкежан", "АӘ"),
            ("777777777777", "zein5934", "Хайбуллин Минтимер", "ХМ"),
        ]
        for iin, password, full_name, initials in extra_admins:
            if not db.query(models.User).filter(models.User.iin == iin).first():
                db.add(models.User(
                    iin=iin,
                    hashed_password=hash_password(password),
                    full_name=full_name,
                    initials=initials,
                    role=models.RoleEnum.admin,
                    is_active=True,
                ))
                print(f"✅ Доп. админ создан: {full_name} ({iin})")
        db.commit()
    finally:
        db.close()

@app.get("/freezing", include_in_schema=False)
def serve_freezing():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freezing.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "freezing.html не найден"}

@app.get("/ent-test", include_in_schema=False)
def serve_ent_test():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ent_test.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "ent_test.html не найден"}

@app.get("/api/public/student/{student_id}")
def get_student_public(student_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import Session
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ученик не найден")
    return {
        "id": student.id,
        "full_name": student.full_name,
        "grade": student.grade,
        "language": student.language,
        "branch": student.branch,
        "status": student.status,
    }

@app.get("/api/public/freezes/{student_id}")
def get_freezes_public(student_id: int, db: Session = Depends(get_db)):
    """История заморозок ученика (для публичной страницы заморозки)."""
    rows = (
        db.query(models.Freeze)
        .filter(models.Freeze.student_id == student_id)
        .order_by(models.Freeze.start_date.desc())
        .all()
    )
    return [
        {
            "id": f.id,
            "start_date": f.start_date.isoformat(),
            "end_date": f.end_date.isoformat(),
            "reason": f.reason,
        }
        for f in rows
    ]

@app.post("/api/public/freezes")
def create_freeze_public(payload: schemas.FreezeCreate, db: Session = Depends(get_db)):
    """Создание заморозки с публичной страницы (по ссылке, без авторизации)."""
    from fastapi import HTTPException
    student = db.query(models.Student).filter(models.Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    fr = models.Freeze(
        student_id=payload.student_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
    )
    db.add(fr)
    db.commit()
    db.refresh(fr)
    # Запись в журнал действий (заморозка оформлена по публичной ссылке)
    try:
        from dependencies import log_action
        class _LinkUser:
            id = None
            full_name = "По ссылке (ученик)"
        log_action(db, _LinkUser(), "create", "freeze", fr.id,
                   f"Заморозка ученика {student.full_name}: {fr.start_date}—{fr.end_date}")
    except Exception:
        pass
    return {"id": fr.id, "detail": "Заморозка оформлена"}

@app.get("/", include_in_schema=False)
def serve_app():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "index.html не найден рядом с main.py"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/debug/tables")
def debug_tables(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        return {
            "status": "connected",
            "database_type": "postgresql" if "postgresql" in str(db.bind.url) else "sqlite",
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/debug/users")  
def debug_users(db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).all()
        return {
            "status": "connected", 
            "user_count": len(users),
            "users": [{"id": u.id, "iin": u.iin, "name": u.full_name, "role": u.role} for u in users]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/debug/connection")
def debug_connection():
    return {
        "status": "app_running",
        "message": "FastAPI работает",
        "database_url_type": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgresql") else "sqlite"
    }
