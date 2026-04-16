from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date, time
from models import RoleEnum, LangEnum, StatusEnum, AttendanceStatus, TaskStatus, DayOfWeek
import re


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    iin: str
    password: str

    @field_validator("iin")
    @classmethod
    def validate_iin(cls, v):
        if not re.match(r"^\d{12}$", v):
            raise ValueError("ИИН должен состоять из 12 цифр")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    full_name: str
    initials: Optional[str] = None
    user_id: int


# ─── User ─────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    iin: str
    full_name: str
    initials: Optional[str] = None
    role: RoleEnum
    phone: Optional[str] = None
    subject: Optional[str] = None
    branch: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    initials: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    branch: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Student ──────────────────────────────────────────────────────────────────

class StudentBase(BaseModel):
    full_name: str
    grade: int
    language: LangEnum
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    branch: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    grade: Optional[int] = None
    language: Optional[LangEnum] = None
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    branch: Optional[str] = None
    status: Optional[StatusEnum] = None

class StudentOut(StudentBase):
    id: int
    status: StatusEnum
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Classroom ────────────────────────────────────────────────────────────────

class ClassroomBase(BaseModel):
    name: str
    capacity: int = 20
    branch: Optional[str] = None
    floor: Optional[int] = None

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    branch: Optional[str] = None
    floor: Optional[int] = None
    is_active: Optional[bool] = None

class ClassroomOut(ClassroomBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}


# ─── Schedule Slot ────────────────────────────────────────────────────────────

class ScheduleSlotBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class ScheduleSlotCreate(ScheduleSlotBase):
    group_id: int

class ScheduleSlotOut(ScheduleSlotBase):
    id: int
    group_id: int
    model_config = {"from_attributes": True}


# ─── Group ────────────────────────────────────────────────────────────────────

class GroupBase(BaseModel):
    name: str
    grade: int
    language: LangEnum
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    capacity: int = 15
    branch: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None
    language: Optional[LangEnum] = None
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[StatusEnum] = None
    branch: Optional[str] = None

class GroupOut(GroupBase):
    id: int
    status: StatusEnum
    created_at: datetime
    student_count: int = 0
    teacher_name: Optional[str] = None
    classroom_name: Optional[str] = None
    schedule_slots: List[ScheduleSlotOut] = []
    model_config = {"from_attributes": True}


# ─── Mentor Assignment ────────────────────────────────────────────────────────

class MentorAssignRequest(BaseModel):
    mentor_id: int
    student_id: int

class MentorAssignOut(BaseModel):
    id: int
    mentor_id: int
    mentor_name: str
    student_id: int
    student_name: str
    assigned_at: datetime
    model_config = {"from_attributes": True}


# ─── Attendance ───────────────────────────────────────────────────────────────

class AttendanceRecord(BaseModel):
    student_id: int
    status: AttendanceStatus
    score_1: Optional[float] = None
    score_2: Optional[float] = None

class AttendanceSaveRequest(BaseModel):
    group_id: int
    date: date
    records: List[AttendanceRecord]

class AttendanceOut(BaseModel):
    id: int
    group_id: int
    student_id: int
    student_name: str
    date: date
    status: AttendanceStatus
    score_1: Optional[float] = None
    score_2: Optional[float] = None
    model_config = {"from_attributes": True}

class AttendanceSummary(BaseModel):
    student_id: int
    student_name: str
    total_lessons: int
    present: int
    absent: int
    attendance_rate: float
    avg_score: Optional[float] = None


# ─── Task ─────────────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None

class TaskOut(TaskBase):
    id: int
    created_by: int
    status: TaskStatus
    created_at: datetime
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None
    model_config = {"from_attributes": True}


# ─── ENT Test ─────────────────────────────────────────────────────────────────

class ENTTestBase(BaseModel):
    name: str
    progress: int = 0

class ENTTestCreate(ENTTestBase):
    pass

class ENTTestUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[StatusEnum] = None
    progress: Optional[int] = None

class ENTTestOut(ENTTestBase):
    id: int
    status: StatusEnum
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Return ───────────────────────────────────────────────────────────────────

class ReturnBase(BaseModel):
    student_name: str
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    language: Optional[LangEnum] = None
    reason: Optional[str] = None
    student_id: Optional[int] = None

class ReturnCreate(ReturnBase):
    pass

class ReturnOut(ReturnBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Enrollment Form ──────────────────────────────────────────────────────────

class EnrollmentFormBase(BaseModel):
    student_name: str
    grade: Optional[int] = None
    language: Optional[LangEnum] = None
    student_phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    branch: Optional[str] = None
    start_date: Optional[date] = None
    payment: Optional[str] = None

class EnrollmentFormCreate(EnrollmentFormBase):
    pass

class EnrollmentFormOut(EnrollmentFormBase):
    id: int
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Forbidden Date ───────────────────────────────────────────────────────────

class ForbiddenDateCreate(BaseModel):
    date: date

class ForbiddenDateOut(BaseModel):
    id: int
    date: date
    added_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_students: int
    active_students: int
    total_groups: int
    active_groups: int
    total_teachers: int
    total_mentors: int
    total_managers: int

class SlotInfo(BaseModel):
    grade: int
    language: LangEnum
    enrolled: int
    capacity: int

class GroupSizeDistribution(BaseModel):
    size: int
    count: int
