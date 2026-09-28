from pydantic import BaseModel, field_validator, model_validator, Field
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
    can_teach: bool = False
    iin: Optional[str] = None


# ─── User ─────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    iin: str
    full_name: str
    initials: Optional[str] = None
    role: RoleEnum
    can_teach: bool = False
    phone: Optional[str] = None
    subject: Optional[str] = None
    hourly_rate: Optional[int] = Field(None, ge=0)
    branch: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @field_validator("iin")
    @classmethod
    def valid_staff_iin(cls, value):
        if not re.fullmatch(r"[0-9]{12}", value):
            raise ValueError("ИИН должен содержать 12 цифр")
        return value

    @field_validator("password")
    @classmethod
    def valid_password(cls, value):
        if not 8 <= len(value.encode("utf-8")) <= 72:
            raise ValueError("Пароль должен занимать от 8 до 72 байт UTF-8")
        return value

class UserUpdate(BaseModel):
    can_teach: Optional[bool] = None
    full_name: Optional[str] = None
    initials: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    hourly_rate: Optional[int] = Field(None, ge=0)
    branch: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def valid_password(cls, value):
        if value is not None and not 8 <= len(value.encode("utf-8")) <= 72:
            raise ValueError("Пароль должен занимать от 8 до 72 байт UTF-8")
        return value

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
    paid_until: Optional[date] = None
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

    @model_validator(mode="after")
    def validate_interval(self):
        if self.end_time <= self.start_time:
            raise ValueError("Окончание урока должно быть позже начала в пределах одного дня")
        if self.start_time.second or self.end_time.second:
            raise ValueError("В расписании указывается время с точностью до минуты")
        return self

class ScheduleSlotCreate(ScheduleSlotBase):
    group_id: int

class ScheduleSlotOut(BaseModel):
    # Read legacy data without applying new write validation. A malformed old
    # slot must not make every group/timetable request fail.
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    id: int
    group_id: int
    model_config = {"from_attributes": True}


# ─── Group ────────────────────────────────────────────────────────────────────

class GroupBase(BaseModel):
    name: str
    subject: Optional[str] = None
    grade: Optional[int] = None
    language: Optional[LangEnum] = None
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    capacity: int = 15
    branch: Optional[str] = None

class GroupCreate(GroupBase):
    schedule: List[ScheduleSlotBase] = Field(default_factory=list, max_length=100)
    student_ids: List[int] = Field(default_factory=list, max_length=1000)

class GroupUpdate(BaseModel):
    schedule: Optional[List[ScheduleSlotBase]] = Field(None, max_length=100)
    name: Optional[str] = None
    subject: Optional[str] = None
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
    student_id: int = Field(gt=0)
    status: AttendanceStatus
    score_1: Optional[float] = Field(None, ge=1, le=10, allow_inf_nan=False)
    score_2: Optional[float] = Field(None, ge=1, le=10, allow_inf_nan=False)

class AttendanceSaveRequest(BaseModel):
    group_id: int = Field(gt=0)
    date: date
    slot_id: Optional[int] = Field(None, gt=0)
    report_id: Optional[int] = Field(None, gt=0)
    expected_revision: int = Field(0, ge=0)
    taught_by: Optional[int] = Field(None, gt=0)
    records: List[AttendanceRecord] = Field(min_length=1, max_length=1000)
    lesson_topic: str = Field(min_length=1, max_length=10000)
    homework: str = Field(min_length=1, max_length=10000)

    @field_validator("lesson_topic", "homework")
    @classmethod
    def trim_required(cls, v):
        if not v.strip():
            raise ValueError("Заполните тему урока и домашнее задание")
        return v.strip()

    @model_validator(mode="after")
    def no_duplicate_students(self):
        ids = [r.student_id for r in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("Ученик повторяется в отчёте")
        return self

class AttendanceOut(BaseModel):
    id: int
    report_id: Optional[int] = None
    group_id: int
    student_id: int
    student_name: str
    date: date
    status: AttendanceStatus
    score_1: Optional[float] = None
    score_2: Optional[float] = None
    lesson_topic: Optional[str] = None
    homework: Optional[str] = None
    recorded_by: Optional[int] = None
    teacher_id: Optional[int] = None
    revision: Optional[int] = None
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


# ─── Freezes (Заморозки) ──────────────────────────────────────────────────────

class FreezeCreate(BaseModel):
    student_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v, info):
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("Дата окончания не может быть раньше начала")
        return v

class FreezeOut(BaseModel):
    id: int
    student_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Audit Log ────────────────────────────────────────────────────────────────

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity: str
    entity_id: Optional[int] = None
    summary: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Характеристики ─────────────────────────────────────────────────────────
class CharacteristicIn(BaseModel):
    student_id: int
    period: str          # YYYY-MM
    text: str = ""

class CharacteristicOut(BaseModel):
    id: int
    student_id: int
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    period: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── Cancelled Lessons ──────────────────────────────────────────────────────
class CancelledLessonIn(BaseModel):
    group_id: int
    date: date
    reason: Optional[str] = None

class CancelledLessonOut(BaseModel):
    id: int
    group_id: int
    date: date
    reason: Optional[str] = None
    cancelled_by: Optional[int] = None
    group_name: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Fines (штрафы преподавателям) ───────────────────────────────────────────
class FineIn(BaseModel):
    teacher_id: int
    amount: int
    reason: Optional[str] = None

class FineOut(BaseModel):
    id: int
    teacher_id: int
    teacher_name: Optional[str] = None
    amount: int
    reason: Optional[str] = None
    issued_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Teacher Substitutions (замена учителя на один день) ───────────────────
class SubstitutionIn(BaseModel):
    group_id: int
    date: date
    substitute_teacher_id: int
    reason: Optional[str] = None

class SubstitutionOut(BaseModel):
    id: int
    group_id: int
    group_name: Optional[str] = None
    date: date
    substitute_teacher_id: int
    substitute_teacher_name: Optional[str] = None
    original_teacher_id: Optional[int] = None
    original_teacher_name: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Transferred Lessons ─────────────────────────────────────────────────────
class TransferLessonIn(BaseModel):
    group_id: int
    date: date
    new_date: date
    reason: Optional[str] = None

class TransferLessonOut(BaseModel):
    id: int
    group_id: int
    date: date
    new_date: date
    reason: Optional[str] = None
    transferred_by: Optional[int] = None
    group_name: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ─── Payments (Оплаты учеников) ──────────────────────────────────────────────
class PaymentIn(BaseModel):
    student_id: int
    start_date: date
    months: int = 0
    gift_months: int = 0
    amount: Optional[int] = None
    note: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    start_date: date
    months: int
    gift_months: int
    amount: Optional[int] = None
    paid_until: date
    note: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}
