"""Business dates must not depend on the server's UTC or browser's timezone."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

BUSINESS_TZ = ZoneInfo(os.getenv("APP_TIMEZONE", "Asia/Almaty"))


def today():
    return datetime.now(BUSINESS_TZ).date()


def local_day(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(BUSINESS_TZ).date()
