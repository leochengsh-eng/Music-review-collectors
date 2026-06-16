from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class ReportWindow:
    start: date
    end: date
    scan_start: date
    scan_end: date
    timezone: str


def previous_tuesday_window(now: datetime | None = None, tz_name: str = "Asia/Shanghai", lookback_days: int = 14) -> ReportWindow:
    tz = ZoneInfo(tz_name)
    current = (now or datetime.now(tz)).astimezone(tz)
    today = current.date()
    days_since_tuesday = (today.weekday() - 1) % 7
    this_week_tuesday = today - timedelta(days=days_since_tuesday)
    if days_since_tuesday == 0 and current.time() < time(10, 0):
        this_week_tuesday -= timedelta(days=7)
    start = this_week_tuesday - timedelta(days=7)
    end = this_week_tuesday - timedelta(days=1)
    return ReportWindow(start=start, end=end, scan_start=today - timedelta(days=lookback_days), scan_end=today, timezone=tz_name)


def in_formal_window(d: date | None, window: ReportWindow) -> bool:
    return bool(d and window.start <= d <= window.end)


def is_late_addition(d: date | None, window: ReportWindow) -> bool:
    return bool(d and window.scan_start <= d <= window.scan_end and not in_formal_window(d, window))
