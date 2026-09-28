"""Non-destructive upgrade of the original SQLite/PostgreSQL database.

Back up the database and run once with the old application stopped. No historical
rows are deleted. A migration failure is fatal, not silently ignored.
"""
from collections import defaultdict, Counter
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
import models

VERSION = "2026_09_lesson_snapshots_v1"
ACCOUNT_ROLES_VERSION = "2026_09_staff_accounts_v2"
ADMIN_TEACHER_IINS = ("000000000001", "222222222222", "333333333333", "444444444444")
ADMIN_ONLY_IINS = ("666666666666",)
RETIRED_ADMIN_IINS = ("555555555555", "777777777777", "888888888888")


def upgrade(engine):
    # Serialize startup migrations between PostgreSQL workers/replicas.
    with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            conn.execute(text("SELECT pg_advisory_xact_lock(2609241001)"))
        existing = set(inspect(conn).get_table_names())
        columns = {
            "users": {"hourly_rate": "INTEGER", "can_teach": "BOOLEAN NOT NULL DEFAULT FALSE"},
            "attendance": {"lesson_topic": "TEXT", "homework": "TEXT", "report_id": "INTEGER REFERENCES lesson_reports(id)"},
            "groups": {"subject": "VARCHAR(150)"},
            "students": {"paid_until": "DATE"},
        }
        # New tables first; create_all skips existing tables/indices.
        models.Base.metadata.create_all(bind=conn)
        for table, additions in columns.items():
            if table not in existing:
                continue
            present = {c["name"] for c in inspect(conn).get_columns(table)}
            for name, ddl in additions.items():
                if name not in present:
                    conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {ddl}'))
        # Indices on tables that already existed are not created by create_all.
        for stmt in (
            "CREATE INDEX IF NOT EXISTS ix_attendance_group_date ON attendance(group_id, date)",
            "CREATE INDEX IF NOT EXISTS ix_attendance_report_student ON attendance(report_id, student_id)",
            "CREATE INDEX IF NOT EXISTS ix_groups_teacher_status ON groups(teacher_id, status)",
            "CREATE INDEX IF NOT EXISTS ix_group_students_group ON group_students(group_id)",
            "CREATE INDEX IF NOT EXISTS ix_group_students_student ON group_students(student_id)",
            "CREATE INDEX IF NOT EXISTS ix_schedule_slots_group_day ON schedule_slots(group_id, day_of_week)",
        ):
            conn.execute(text(stmt))
        with Session(bind=conn) as db:
            # Keep retired users as inactive rows so old lesson/report authorship remains intact.
            if not db.get(models.SchemaMigration, ACCOUNT_ROLES_VERSION):
                for user in db.query(models.User).all():
                    if user.iin in ADMIN_TEACHER_IINS:
                        user.role = models.RoleEnum.admin
                        user.can_teach = True
                        user.is_active = True
                    elif user.iin in ADMIN_ONLY_IINS:
                        user.role = models.RoleEnum.admin
                        user.can_teach = False
                        user.is_active = True
                    elif user.iin in RETIRED_ADMIN_IINS:
                        user.can_teach = False
                        user.is_active = False
                db.add(models.SchemaMigration(version=ACCOUNT_ROLES_VERSION))
                db.flush()
            if db.get(models.SchemaMigration, VERSION):
                return
            for user in db.query(models.User).all():
                if user.role == models.RoleEnum.teacher or (
                    user.role == models.RoleEnum.admin and user.iin in ADMIN_TEACHER_IINS
                ):
                    user.can_teach = True
            db.flush()
            users = {u.id: u for u in db.query(models.User).all()}
            groups = {g.id: g for g in db.query(models.Group).all()}
            grouped = defaultdict(list)
            for row in db.query(models.Attendance).filter(models.Attendance.report_id.is_(None)).order_by(models.Attendance.id):
                grouped[(row.group_id, row.date)].append(row)
            for (gid, day), rows in grouped.items():
                group = groups.get(gid)
                if group is None:
                    raise RuntimeError(f"Attendance references missing group {gid}; restore it before migration")
                authors = {r.recorded_by for r in rows}
                author_id = next(iter(authors)) if len(authors) == 1 else None
                author = users.get(author_id)
                notes = []
                if author is None:
                    notes.append("Автор отсутствует или в старых строках указаны разные авторы; не назначен текущий учитель группы")
                elif author.role != models.RoleEnum.teacher:
                    notes.append("Исторический отчёт заполнен администратором/сотрудником: проверьте, кто фактически проводил урок")
                if any(n > 1 for n in Counter(r.student_id for r in rows).values()):
                    notes.append("В старом журнале дубли учеников; исходные строки сохранены")
                report = models.LessonReport(
                    group_id=gid, date=day, slot_key="legacy", teacher_id=author.id if author else None,
                    teacher_name=author.full_name if author else "Неизвестный преподаватель",
                    group_name=group.name, subject=group.subject,
                    language=group.language.value if group.language else None,
                    lesson_rate=author.hourly_rate if author else None,
                    lesson_topic=next((r.lesson_topic for r in rows if r.lesson_topic), None),
                    homework=next((r.homework for r in rows if r.homework), None),
                    recorded_by=author.id if author else None, updated_by=author.id if author else None,
                    revision=1, needs_review=bool(notes), provenance="legacy_recorded_by",
                    review_note="; ".join(notes) or None,
                    created_at=rows[0].created_at,
                )
                db.add(report)
                db.flush()
                for row in rows:
                    row.report_id = report.id
            db.add(models.SchemaMigration(version=VERSION))
            db.flush()


if __name__ == "__main__":
    from database import engine
    upgrade(engine)
    print("Migration completed; original attendance rows preserved.")
