from __future__ import annotations
try:
    import feedparser
except ModuleNotFoundError:
    feedparser = None
from src.models import SourceRunStatus, ReviewItem
from src.parsers.base import parse_feed_entry


def _manual_item(source: dict, url: str, reason: str, title: str | None = None) -> ReviewItem:
    return ReviewItem(
        artist="Unknown Artist",
        album=title or "Manual review required",
        release_type="unknown",
        review_source=source["name"],
        review_url=url,
        status="manual_check",
        parse_status="parse_failed",
        manual_check_reason=reason,
        confidence="low",
    )


def collect_rss(source: dict, timeout: int = 20) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if feedparser is None:
            reason = "feedparser dependency is not installed"
            return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source_name=source["name"], status="failed", error_message=reason, items_failed=1)
        feed = feedparser.parse(source.get("url", ""), request_headers={"User-Agent": "AlbumReviewDigest/0.1 (+respectful; no paywall bypass)"})
        entries = list(getattr(feed, "entries", []) or [])[:50]
        items: list[ReviewItem] = []
        failed = 0
        for entry in entries:
            try:
                item = parse_feed_entry(entry, source)
                if not item.review_url:
                    raise ValueError("missing entry URL")
                items.append(item)
            except Exception as exc:
                failed += 1
                title = entry.get("title", "Manual review required") if hasattr(entry, "get") else "Manual review required"
                url = entry.get("link", source.get("url", "")) if hasattr(entry, "get") else source.get("url", "")
                items.append(_manual_item(source, url, f"RSS parse failure: {exc}", title))
        status = "partial_success" if failed or getattr(feed, "bozo", False) else "success"
        error = str(getattr(feed, "bozo_exception", "")) or None if getattr(feed, "bozo", False) else None
        if not entries:
            status = "zero_items"
            error = "RSS feed returned zero entries"
        return items, SourceRunStatus(source_name=source["name"], status=status, items_found=len(entries), items_parsed=len(items)-failed, items_failed=failed, error_message=error)
    except Exception as exc:
        reason = str(exc)
        return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source_name=source["name"], status="failed", error_message=reason, items_failed=1)
