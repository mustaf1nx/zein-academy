"""
Zein Academy — Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
import models, os
from auth import hash_password


from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.students import router as students_router
from routers.groups import router as groups_router
from routers.classrooms import router as classrooms_router
from routers.attendance import router as attendance_router
from routers.extra import (
    tasks_router, returns_router, forms_router, ent_router,
    forbidden_router, mentors_router, analytics_router,
)

models.Base.metadata.create_all(bind=engine)

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


@app.on_event("startup")
def seed_default_admin():
    db = SessionLocal()
    try:
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
    finally:
        db.close()

@app.get("/freezing", include_in_schema=False)
def serve_freezing():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freezing.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "freezing.html не найден"}

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

@app.get("/", include_in_schema=False)
def serve_app():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "index.html не найден рядом с main.py"}


@app.get("/health")
def health():
    return {"status": "healthy"}