"""Create missing staff only; never reset existing names, passwords or activation.

New secrets are either supplied through the environment or written to a private
local credentials file. No passwords are printed to application logs.
"""
from pathlib import Path
from datetime import datetime, timezone
import os
import json
import secrets
import models
from auth import hash_password

ACCOUNTS = (
    ("900101350123", "Администратор", "АД", False, "INITIAL_ADMIN_PASSWORD"),
    ("666666666666", "Айдынұлы Әкежан", "АӘ", False, "ADMIN_PASSWORD_666666666666"),
    ("000000000001", "Админ-преподаватель 1", "АП1", True, "ADMIN_TEACHER_1_PASSWORD"),
    ("222222222222", "Админ-преподаватель 2", "АП2", True, "ADMIN_TEACHER_2_PASSWORD"),
    ("333333333333", "Админ-преподаватель 3", "АП3", True, "ADMIN_TEACHER_3_PASSWORD"),
    ("444444444444", "Админ-преподаватель 4", "АП4", True, "ADMIN_TEACHER_4_PASSWORD"),
)


def seed_accounts(db, credentials_dir=None):
    new_credentials = []
    path = None
    try:
        for iin, name, initials, teaching, env_key in ACCOUNTS:
            existing = db.query(models.User).filter_by(iin=iin).first()
            if existing:
                # Preserve the person's name/password, but enforce the configured access level.
                existing.role = models.RoleEnum.admin
                existing.can_teach = teaching
                existing.is_active = True
                continue
            password = os.getenv(env_key) or secrets.token_urlsafe(18)
            db.add(models.User(iin=iin, full_name=name, initials=initials,
                hashed_password=hash_password(password), role=models.RoleEnum.admin,
                can_teach=teaching, is_active=True))
            # Environment-supplied passwords need not be copied to disk.
            if not os.getenv(env_key):
                new_credentials.append({"iin": iin, "full_name": name, "password": password, "can_teach": teaching})
        if new_credentials:
            directory = Path(credentials_dir or os.getenv("CREDENTIALS_DIR", ".secrets"))
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            path = directory / ("initial_accounts_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + secrets.token_hex(4) + ".json")
            with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as f:
                json.dump(new_credentials, f, ensure_ascii=False, indent=2)
        db.commit()
    except Exception:
        db.rollback()
        if path:
            path.unlink(missing_ok=True)
        raise
    if path:
        print(f"Created missing accounts. Initial credentials stored privately in {path}; move them to a password manager and remove the file.")
    return path
