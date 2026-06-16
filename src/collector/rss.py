from __future__ import annotations
try:
    import feedparser
except ModuleNotFoundError:
    feedparser = None
from src.models import SourceRunStatus, ReviewItem
from src.parsers.base import parse_feed_entry


def collect_rss(source: dict, timeout: int = 20) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if feedparser is None:
            return [], SourceRunStatus(source_name=source["name"], status="failed", error_message="feedparser dependency is not installed", items_failed=1)
        feed = feedparser.parse(source.get("url", ""), request_headers={"User-Agent": "AlbumReviewDigest/0.1 (+respectful; no paywall bypass)"})
        items = [parse_feed_entry(e, source) for e in feed.entries[:50]]
        status = "partial_success" if getattr(feed, "bozo", False) else "success"
        return items, SourceRunStatus(source_name=source["name"], status=status, items_found=len(feed.entries), items_parsed=len(items), items_failed=0)
    except Exception as exc:
        return [], SourceRunStatus(source_name=source["name"], status="failed", error_message=str(exc), items_failed=1)
