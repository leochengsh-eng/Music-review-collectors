from __future__ import annotations
from datetime import datetime
from email.utils import parsedate_to_datetime

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    BeautifulSoup = None
from src.models import ReviewItem
from src.normalize.scores import normalize_score


def parse_date(value):
    if not value: return None
    if isinstance(value, datetime): return value.date()
    try: return parsedate_to_datetime(str(value)).date()
    except Exception: pass
    try: return datetime.fromisoformat(str(value).replace('Z','+00:00')).date()
    except Exception: return None


def split_title(title: str) -> tuple[str, str]:
    for sep in [" – ", " — ", " - ", ": "]:
        if sep in title:
            a, b = title.split(sep, 1)
            return a.strip(), b.strip()
    return "Unknown Artist", title.strip() or "Unknown Album"


def extract_score(text: str, scale: int | None):
    import re
    patterns = [r"\b\d+(?:\.\d)?\s*/\s*10\b", r"\b[0-5](?:\.5)?\s*/\s*5\b", r"\b\d{2,3}\s*/\s*100\b"]
    for p in patterns:
        m = re.search(p, text or "")
        if m:
            raw = m.group(0)
            return raw, normalize_score(raw, None)
    return None, None


def parse_feed_entry(entry, source: dict) -> ReviewItem:
    title = getattr(entry, "title", "") or entry.get("title", "")
    artist, album = split_title(title)
    raw_summary = entry.get("summary", "") or entry.get("description", "")
    summary = BeautifulSoup(raw_summary, "html.parser").get_text(" ") if BeautifulSoup else raw_summary
    raw, norm = extract_score(" ".join([title, summary]), source.get("score_scale"))
    item = ReviewItem(artist=artist, album=album, release_type="album", review_source=source["name"], review_url=entry.get("link", ""), review_date=parse_date(entry.get("published") or entry.get("updated")), publication_date=parse_date(entry.get("published") or entry.get("updated")), raw_score=raw, normalized_score_10=norm, score_source=source["name"] if raw else None, score_status="scored" if raw else "no_score")
    if raw:
        item.all_scores.append(__import__('src.models', fromlist=['Score']).Score(source=source['name'], raw=raw, normalized_10=norm, url=item.review_url))
    if source.get("id") == "pitchfork" and not raw:
        item.reason_for_inclusion = "pitchfork_discovery_no_score"
    return item


def parse_listing_card(title: str, url: str, source: dict) -> ReviewItem:
    artist, album = split_title(title)
    raw, norm = extract_score(title, source.get("score_scale"))
    return ReviewItem(artist=artist, album=album, release_type="album", review_source=source["name"], review_url=url, raw_score=raw, normalized_score_10=norm, score_source=source["name"] if raw else None, score_status="scored" if raw else "no_score", status="aggregator_find" if "reverse_lookup" in source.get("role", []) else "new_review", reason_for_inclusion="aggregator_find" if "reverse_lookup" in source.get("role", []) else "discovered_review")
