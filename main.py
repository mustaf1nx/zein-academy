"""
Zein Academy — Backend API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from dependencies import require_admin, get_current_user
from migrations import upgrade
from bootstrap import seed_accounts
from routers.lessons import router as lessons_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
import models, os
import schemas
from auth import hash_password
from share_links import verify_freeze_token, check_freeze_overlap
from clock import today


from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.students import router as students_router
from routers.groups import router as groups_router
from routers.classrooms import router as classrooms_router
from routers.attendance import router as attendance_router
from routers.extra import (
    tasks_router, returns_router, forms_router, ent_router,
    forbidden_router, mentors_router, analytics_router, freezes_router, audit_router,
    characteristics_router, cancelled_router, transfer_router, fines_router,
    substitutions_router, payments_router,
)

# Additive, transactional and idempotent. Stop on migration errors.
upgrade(engine)

app = FastAPI(title="Zein Academy API", version="1.1.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "").split(",") if x.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
app.include_router(lessons_router)

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
app.include_router(cancelled_router)
app.include_router(transfer_router)
app.include_router(fines_router)
app.include_router(substitutions_router)
app.include_router(payments_router)

# Статические файлы (логотипы и пр.)
_assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")


@app.on_event("startup")
def seed_default_admin():
    if os.getenv("SEED_ACCOUNTS", "true").lower() not in {"1", "true", "yes"}:
        return
    with SessionLocal() as db:
        seed_accounts(db)


@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    elif request.url.path in {"/", "/freezing", "/ent-test"}:
        response.headers["Cache-Control"] = "no-cache"
    return response

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
def get_student_public(student_id: int, token: str | None = None, db: Session = Depends(get_db)):
    verify_freeze_token(token, student_id)
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
def get_freezes_public(student_id: int, token: str | None = None, db: Session = Depends(get_db)):
    """История только владельцу подписанной ссылки."""
    verify_freeze_token(token, student_id)
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
def create_freeze_public(payload: schemas.FreezeCreate, token: str | None = None, db: Session = Depends(get_db)):
    """Create only for the student identified by the expiring signed link."""
    verify_freeze_token(token, payload.student_id)
    if payload.start_date < today():
        raise HTTPException(422, "По ссылке нельзя оформлять заморозку задним числом; обратитесь к администратору")
    student = db.query(models.Student).filter(models.Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    check_freeze_overlap(db, payload.student_id, payload.start_date, payload.end_date)
    fr = models.Freeze(
        student_id=payload.student_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
    )
    db.add(fr)
    db.flush()
    from routers.extra import recompute_student_paid_until
    recompute_student_paid_until(db, payload.student_id)
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
def debug_tables(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
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
def debug_users(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
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
def debug_connection(_: models.User = Depends(require_admin)):
    return {
        "status": "app_running",
        "message": "FastAPI работает",
        "database_url_type": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgresql") else "sqlite"
    }
