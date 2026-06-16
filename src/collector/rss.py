from __future__ import annotations
try:
    import feedparser
except ModuleNotFoundError:
    feedparser = None
from src.models import SourceRunStatus, ReviewItem
from src.parsers.base import parse_feed_entry


def _manual_parse_item(source: dict, url: str, reason: str) -> ReviewItem:
    return ReviewItem(
        artist="Manual Check",
        album=f"{source.get('name', 'Unknown source')} feed item",
        release_type="unknown",
        review_source=source.get("name", "Unknown source"),
        review_url=url,
        status="manual_check",
        parse_status="parse_failed",
        manual_check_reason=reason,
        confidence="low",
    )


def collect_rss(source: dict, timeout: int = 20) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if feedparser is None:
            return [], SourceRunStatus(source_name=source["name"], status="failed", error_message="feedparser dependency is not installed", items_failed=1)
        feed = feedparser.parse(source.get("url", ""), request_headers={"User-Agent": "AlbumReviewDigest/0.1 (+respectful; no paywall bypass)"})
        items = []
        failed = 0
        entries = list(feed.entries[:50])
        for entry in entries:
            try:
                item = parse_feed_entry(entry, source)
                if not item.review_url:
                    item.status = "manual_check"
                    item.parse_status = "parse_failed"
                    item.manual_check_reason = "missing_review_url"
                items.append(item)
            except Exception as exc:
                failed += 1
                items.append(_manual_parse_item(source, entry.get("link", source.get("url", "")), str(exc)))
        if not entries:
            return items, SourceRunStatus(source_name=source["name"], status="zero_items", items_found=0, items_parsed=0, items_failed=0, error_message="RSS feed returned zero entries")
        status = "partial_success" if failed or getattr(feed, "bozo", False) else "success"
        error_message = str(getattr(feed, "bozo_exception", "")) or None if getattr(feed, "bozo", False) else None
        return items, SourceRunStatus(source_name=source["name"], status=status, items_found=len(entries), items_parsed=len(items)-failed, items_failed=failed, error_message=error_message)
    except Exception as exc:
        return [], SourceRunStatus(source_name=source["name"], status="failed", error_message=str(exc), items_failed=1)
