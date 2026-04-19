from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time,
    ForeignKey, Text, Float, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base
from datetime import datetime


class UniversalJSON(TypeDecorator):
    """JSON тип который работает с PostgreSQL и SQLite"""
    impl = Text
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSON())
        else:
            return dialect.type_descriptor(Text())
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        import json
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        import json
        return json.loads(value)


# ─── Enums ───────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    mentor = "mentor"
    manager = "manager"
    lidoruby = "lidoruby"

class LangEnum(str, enum.Enum):
    KAZ = "KAZ"
    RUS = "RUS"

class StatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    none = "none"

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class DayOfWeek(str, enum.Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"


# ─── Users (Staff) ────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    iin = Column(String(12), unique=True, index=True, nullable=False)  # Казахский ИИН
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(200), nullable=False)
    initials = Column(String(10))
    role = Column(SAEnum(RoleEnum), nullable=False)
    phone = Column(String(20))
    subject = Column(String(100))          # для учителей
    branch = Column(String(100))           # филиал
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    groups_taught = relationship("Group", back_populates="teacher", foreign_keys="Group.teacher_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    mentor_assignments = relationship("MentorAssignment", back_populates="mentor", foreign_keys="MentorAssignment.mentor_id")
    form_history = relationship("EnrollmentForm", back_populates="manager")


# ─── Students ─────────────────────────────────────────────────────────────────

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    grade = Column(Integer, nullable=False)         # класс (1-12)
    language = Column(SAEnum(LangEnum), nullable=False)
    phone = Column(String(20))
    parent_name = Column(String(200))
    parent_phone = Column(String(20))
    branch = Column(String(100))
    status = Column(SAEnum(StatusEnum), default=StatusEnum.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group_memberships = relationship("GroupStudent", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    mentor_assignment = relationship("MentorAssignment", back_populates="student", uselist=False)
    returns = relationship("Return", back_populates="student")


# ─── Classrooms ───────────────────────────────────────────────────────────────

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=20)
    branch = Column(String(100))
    floor = Column(Integer)
    is_active = Column(Boolean, default=True)

    groups = relationship("Group", back_populates="classroom")


# ─── Groups ───────────────────────────────────────────────────────────────────

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)
    language = Column(SAEnum(LangEnum), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    capacity = Column(Integer, default=15)
    status = Column(SAEnum(StatusEnum), default=StatusEnum.ACTIVE)
    branch = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("User", back_populates="groups_taught", foreign_keys=[teacher_id])
    classroom = relationship("Classroom", back_populates="groups")
    students = relationship("GroupStudent", back_populates="group")
    schedule_slots = relationship("ScheduleSlot", back_populates="group", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="group")


class GroupStudent(Base):
    """M2M: student ↔ group"""
    __tablename__ = "group_students"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="students")
    student = relationship("Student", back_populates="group_memberships")


# ─── Mentor Assignments ───────────────────────────────────────────────────────

class MentorAssignment(Base):
    __tablename__ = "mentor_assignments"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    mentor = relationship("User", back_populates="mentor_assignments", foreign_keys=[mentor_id])
    student = relationship("Student", back_populates="mentor_assignment")


# ─── Schedule ─────────────────────────────────────────────────────────────────

class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    day_of_week = Column(SAEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    group = relationship("Group", back_populates="schedule_slots")


# ─── Attendance ───────────────────────────────────────────────────────────────

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SAEnum(AttendanceStatus), default=AttendanceStatus.none)
    score_1 = Column(Float, nullable=True)   # оценка 1
    score_2 = Column(Float, nullable=True)   # оценка 2
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")


# ─── Tasks ────────────────────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.todo)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])


# ─── ENT Tests ────────────────────────────────────────────────────────────────

class ENTTest(Base):
    __tablename__ = "ent_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    status = Column(SAEnum(StatusEnum), default=StatusEnum.ACTIVE)
    progress = Column(Integer, default=0)   # 0–100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    correct_answers = Column(UniversalJSON, default={})



# ─── ENT results ────────────────────────────────────────────────────────────────
class ENTStudentResult(Base):
    __tablename__ = "ent_student_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("ent_tests.id"))
    student_name = Column(String)
    student_phone = Column(String, nullable=True)
    grade = Column(Integer)
    language = Column(String, default="RUS")
    subject1 = Column(String, nullable=True)
    subject2 = Column(String, nullable=True)
    answers = Column(UniversalJSON, default={})
    scores = Column(UniversalJSON, default={})
    total_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Returns (Возвраты) ───────────────────────────────────────────────────────

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    student_name = Column(String(200), nullable=False)
    parent_name = Column(String(200))
    parent_phone = Column(String(20))
    language = Column(SAEnum(LangEnum))
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="returns")


# ─── Enrollment Forms (История форм) ──────────────────────────────────────────

class EnrollmentForm(Base):
    __tablename__ = "enrollment_forms"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    student_name = Column(String(200), nullable=False)
    grade = Column(Integer)
    language = Column(SAEnum(LangEnum))
    student_phone = Column(String(20))
    parent_name = Column(String(200))
    parent_phone = Column(String(20))
    branch = Column(String(100))
    start_date = Column(Date, nullable=True)
    payment = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("User", back_populates="form_history")


# ─── Forbidden Dates (Запрещённые даты) ──────────────────────────────────────

class ForbiddenDate(Base):
    __tablename__ = "forbidden_dates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    added_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
