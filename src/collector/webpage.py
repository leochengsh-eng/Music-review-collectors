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


def _is_relevant_link(href: str, source: dict) -> bool:
    source_id = source.get("id")
    if source_id == "album_of_the_year":
        return "/album/" in href
    if source_id == "metacritic":
        return "/music/" in href
    return True


def _manual_parse_item(source: dict, url: str, reason: str) -> ReviewItem:
    return ReviewItem(
        artist="Manual Check",
        album=f"{source.get('name', 'Unknown source')} listing item",
        release_type="unknown",
        review_source=source.get("name", "Unknown source"),
        review_url=url,
        status="manual_check",
        parse_status="parse_failed",
        manual_check_reason=reason,
        confidence="low",
    )


def collect_webpage(source: dict) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if requests is None or BeautifulSoup is None:
            return [], SourceRunStatus(source["name"], "failed", error_message="requests/beautifulsoup dependency is not installed", items_failed=1)
        resp = requests.get(source.get("url", ""), timeout=20, headers={"User-Agent": "AlbumReviewDigest/0.1 (+respectful; no paywall bypass)"})
        if resp.status_code in {401, 403}: return [], SourceRunStatus(source["name"], "blocked", error_message=f"HTTP {resp.status_code}", items_failed=1)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items=[]; failed=0; seen=set(); found=0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not _is_relevant_link(href, source):
                continue
            text = a.get_text(" ", strip=True)
            url = requests.compat.urljoin(source.get("url", ""), href)
            if url in seen or len(text) <= 3:
                continue
            seen.add(url); found += 1
            try:
                items.append(parse_listing_card(text, url, source))
            except Exception as exc:
                failed += 1
                items.append(_manual_parse_item(source, url, str(exc)))
            if len(items) >= 25:
                break
        if not items:
            return [], SourceRunStatus(source["name"], "zero_items", items_found=found, items_parsed=0, items_failed=0, error_message="Listing returned zero parseable album links")
        status = "partial_success" if failed else "success"
        return items, SourceRunStatus(source["name"], status, items_found=found, items_parsed=len(items)-failed, items_failed=failed)
    except Exception as exc:
        return [], SourceRunStatus(source["name"], "failed", error_message=str(exc), items_failed=1)
