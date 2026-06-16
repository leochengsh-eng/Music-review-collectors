from __future__ import annotations
import os
try:
    import yaml
except ModuleNotFoundError:
    yaml = None
from dataclasses import dataclass
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

@dataclass
class Settings:
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    email_from: str | None
    email_to: str
    report_timezone: str
    report_lookback_days: int
    include_types: list[str]


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        smtp_host=os.getenv("SMTP_HOST"), smtp_port=int(os.getenv("SMTP_PORT", "587") or 587),
        smtp_username=os.getenv("SMTP_USERNAME"), smtp_password=os.getenv("SMTP_PASSWORD"),
        email_from=os.getenv("EMAIL_FROM"), email_to=os.getenv("EMAIL_TO", "leochengsh@gmail.com"),
        report_timezone=os.getenv("REPORT_TIMEZONE", "Asia/Shanghai"),
        report_lookback_days=int(os.getenv("REPORT_LOOKBACK_DAYS", "14")),
        include_types=[x.strip() for x in os.getenv("INCLUDE_TYPES", "album,ep,reissue,sunday_review").split(",") if x.strip()],
    )


def load_sources(path: str = "sources.yaml") -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        if yaml:
            return yaml.safe_load(fh).get("sources", [])
        return []
