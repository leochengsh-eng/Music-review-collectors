from __future__ import annotations

import re

SOURCE_THRESHOLDS = {
    "pitchfork": 7.0,
    "guardian": 8.0,
    "allmusic": 7.0,
}


def normalize_score(raw_score: str | int | float | None, scale: int | float | None = None) -> float | None:
    if raw_score is None or raw_score == "":
        return None
    if isinstance(raw_score, (int, float)):
        value = float(raw_score)
    else:
        text = str(raw_score).strip().lower()
        stars = re.search(r"([0-5](?:\.5)?)\s*/\s*5", text)
        hundred = re.search(r"(\d{1,3})\s*/\s*100", text)
        ten = re.search(r"(\d{1,2}(?:\.\d)?)\s*/\s*10", text)
        if hundred:
            return round(float(hundred.group(1)) / 10, 1)
        if stars:
            return round(float(stars.group(1)) * 2, 1)
        if ten:
            return round(float(ten.group(1)), 1)
        match = re.search(r"\d+(?:\.\d)?", text)
        if not match:
            return None
        value = float(match.group(0))
    if scale:
        return round(value / float(scale) * 10, 1)
    if value > 10:
        return round(value / 10, 1)
    return round(value, 1)


def is_recommendation(score: float | None, source_id: str | None = None) -> bool:
    if score is None:
        return False
    threshold = SOURCE_THRESHOLDS.get((source_id or "").lower(), 7.0)
    return score >= threshold
