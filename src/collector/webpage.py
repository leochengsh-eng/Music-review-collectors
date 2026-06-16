from __future__ import annotations
try:
    import requests
except ModuleNotFoundError:
    requests = None
try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    BeautifulSoup = None
from src.models import SourceRunStatus, ReviewItem
from src.parsers.base import parse_listing_card


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


def _candidate_links(soup, source: dict):
    source_id = source.get("id")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        if len(text) < 8:
            continue
        if source_id == "album_of_the_year" and not ("/album/" in href or "/release/" in href):
            continue
        if source_id == "metacritic" and "/music/" not in href:
            continue
        yield text, requests.compat.urljoin(source.get("url", ""), href)


def collect_webpage(source: dict) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if requests is None or BeautifulSoup is None:
            reason = "requests/beautifulsoup dependency is not installed"
            return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source["name"], "failed", error_message=reason, items_failed=1)
        resp = requests.get(source.get("url", ""), timeout=20, headers={"User-Agent": "Mozilla/5.0 AlbumReviewDigest/0.1 (+respectful; no paywall bypass)", "Accept": "text/html,application/xhtml+xml"})
        if resp.status_code in {401, 403, 429}:
            reason = f"HTTP {resp.status_code} blocked or rate-limited"
            return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source["name"], "blocked", error_message=reason, items_failed=1)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items=[]; failed=0; seen=set()
        for text, url in _candidate_links(soup, source):
            if url in seen:
                continue
            seen.add(url)
            try:
                item = parse_listing_card(text, url, source)
                if not item.album or item.album == "Unknown Album":
                    raise ValueError("could not identify album from listing text")
                items.append(item)
            except Exception as exc:
                failed += 1
                items.append(_manual_item(source, url, f"Listing parse failure: {exc}", text))
            if len(items) >= 25:
                break
        if not items:
            reason = "listing returned zero parseable candidate items"
            return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source["name"], "zero_items", items_found=0, items_parsed=0, items_failed=1, error_message=reason)
        status = "partial_success" if failed else "success"
        return items, SourceRunStatus(source["name"], status, items_found=len(seen), items_parsed=len(items)-failed, items_failed=failed)
    except Exception as exc:
        reason = str(exc)
        return [_manual_item(source, source.get("url", ""), reason)], SourceRunStatus(source["name"], "failed", error_message=reason, items_failed=1)
