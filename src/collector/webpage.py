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


def collect_webpage(source: dict) -> tuple[list[ReviewItem], SourceRunStatus]:
    try:
        if requests is None or BeautifulSoup is None:
            return [], SourceRunStatus(source["name"], "failed", error_message="requests/beautifulsoup dependency is not installed", items_failed=1)
        resp = requests.get(source.get("url", ""), timeout=20, headers={"User-Agent": "AlbumReviewDigest/0.1 (+respectful; no paywall bypass)"})
        if resp.status_code in {401, 403}: return [], SourceRunStatus(source["name"], "blocked", error_message=f"HTTP {resp.status_code}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items=[]
        for a in soup.find_all("a", href=True)[:80]:
            text = a.get_text(" ", strip=True)
            if len(text) > 8:
                items.append(parse_listing_card(text, requests.compat.urljoin(source.get("url", ""), a["href"]), source))
        return items[:25], SourceRunStatus(source["name"], "success", items_found=len(items), items_parsed=min(len(items),25))
    except Exception as exc:
        return [], SourceRunStatus(source["name"], "failed", error_message=str(exc), items_failed=1)
