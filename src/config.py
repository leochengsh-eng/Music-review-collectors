from __future__ import annotations
import os
try:
    import yaml
except ModuleNotFoundError:
    yaml = None
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False
from dataclasses import dataclass

@dataclass
class Settings:
    report_timezone: str
    report_lookback_days: int
    include_types: list[str]
    delivery_mode: str = "pages"


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        report_timezone=os.getenv("REPORT_TIMEZONE", "Asia/Shanghai"),
        report_lookback_days=int(os.getenv("REPORT_LOOKBACK_DAYS", "14")),
        include_types=[x.strip() for x in os.getenv("INCLUDE_TYPES", "album,ep,reissue,sunday_review").split(",") if x.strip()],
        delivery_mode=os.getenv("DELIVERY_MODE", "pages"),
    )


def load_sources(path: str = "sources.yaml") -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        if yaml:
            return yaml.safe_load(fh).get("sources", [])
        return []
