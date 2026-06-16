from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any


@dataclass
class Score:
    source: str
    raw: str | None
    normalized_10: float | None
    url: str | None = None


@dataclass
class ReviewItem:
    artist: str
    album: str
    release_type: str = "unknown"
    review_source: str = ""
    review_url: str = ""
    review_date: date | None = None
    publication_date: date | None = None
    author: str | None = None
    raw_score: str | None = None
    normalized_score_10: float | None = None
    score_source: str | None = None
    all_scores: list[Score] = field(default_factory=list)
    genre_bucket: str = "Unknown"
    subgenre: str | None = None
    genre_confidence: str = "low"
    recommended_track: str | None = None
    brief_review_cn: str = "资料有限，保留为本周新发现条目。"
    reason_for_inclusion: str = "discovered_review"
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    status: str = "new_review"
    parse_status: str = "success"
    score_status: str = "no_score"
    dedupe_status: str = "unique"
    confidence: str = "medium"
    manual_check_reason: str | None = None
    summary_confidence: str = "low"
    excluded_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("review_date", "publication_date"):
            if data[key]:
                data[key] = data[key].isoformat()
        for key in ("first_seen_at", "last_seen_at"):
            if data[key]:
                data[key] = data[key].isoformat()
        return data


@dataclass
class SourceRunStatus:
    source_name: str
    status: str
    items_found: int = 0
    items_parsed: int = 0
    items_failed: int = 0
    error_message: str | None = None
    last_success_at: datetime | None = None
