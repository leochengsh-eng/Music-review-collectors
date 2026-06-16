from __future__ import annotations
from html import escape
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ModuleNotFoundError:
    Environment = FileSystemLoader = select_autoescape = None
from src.utils.dates import ReportWindow, in_formal_window, is_late_addition


def build_sections(items: list[dict], window: ReportWindow, source_statuses: list[dict] | None = None):
    recommended=[i for i in items if (i.get('normalized_score_10') or 0) >= 7 and i.get('status') != 'manual_check']
    by_genre={g: [] for g in ["Pop","Rock","Electronic","R&B / Soul","Folk / Country","Global / C-Pop","Unknown"]}
    for i in recommended: by_genre.setdefault(i.get('genre_bucket') or 'Unknown', []).append(i)
    manual=[i for i in items if i.get('status')=='manual_check' or i.get('parse_status')!='success' or i.get('dedupe_status')=='uncertain']
    aggregators=[i for i in items if i.get('status')=='aggregator_find']
    late=[i for i in items if is_late_addition(__import__('datetime').date.fromisoformat(i['review_date']) if i.get('review_date') else None, window)]
    new=[i for i in items if i.get('status') not in {'manual_check', 'aggregator_find'} and in_formal_window(__import__('datetime').date.fromisoformat(i['review_date']) if i.get('review_date') else window.start, window)]
    statuses = source_statuses or []
    no_real_data = not new and not aggregators
    return {"recommended": recommended, "by_genre": by_genre, "manual": manual, "aggregators": aggregators, "late": late, "new": new, "source_statuses": statuses, "no_real_data": no_real_data}


def _fallback_html(items: list[dict], window: ReportWindow, source_statuses: list[dict] | None = None) -> str:
    sections = build_sections(items, window, source_statuses)
    cards = "".join(
        f'<div class="card"><b>{escape(str(i.get("artist") or "Unknown artist"))} — {escape(str(i.get("album") or "Unknown album"))}</b>'
        f'<span>{escape(str(i.get("normalized_score_10") if i.get("normalized_score_10") is not None else "—"))}/10</span></div>'
        for i in items
    )
    status_rows = "".join(
        f'<li>{escape(str(s.get("source_name")))}: {escape(str(s.get("status")))} — found {escape(str(s.get("items_found", 0)))}, parsed {escape(str(s.get("items_parsed", 0)))} {escape(str(s.get("error_message") or ""))}</li>'
        for s in sections["source_statuses"]
    )
    empty = '<p>No valid real album reviews or aggregator finds were collected for this report period.</p>' if sections["no_real_data"] else ''
    return f"<!doctype html><html><body><h1>Album Review Weekly Digest</h1><p>{window.start} to {window.end}</p>{empty}{cards}<h2>Source Status</h2><ul>{status_rows}</ul></body></html>"


def _render_archive_page(report_paths: list[Path], docs_dir: Path) -> str:
    links = []
    for path in sorted(report_paths, reverse=True):
        label = path.stem.replace("album-review-digest-", "").replace("_to_", " to ")
        href = path.relative_to(docs_dir).as_posix()
        links.append(f'<li><a href="{escape(href)}">{escape(label)}</a></li>')
    body = "\n".join(links) or "<li>No reports generated yet.</li>"
    return f"<!doctype html><html><body><h1>Album Review Archive</h1><ul>{body}</ul></body></html>\n"


def _render_index_page(latest_report: Path | None, docs_dir: Path) -> str:
    if latest_report:
        latest_href = latest_report.relative_to(docs_dir).as_posix()
        latest_link = f'<p><a href="{escape(latest_href)}">Open the latest weekly report</a></p>'
    else:
        latest_link = "<p>No weekly reports generated yet.</p>"
    return f"<!doctype html><html><body><h1>Album Review Weekly Digest</h1>{latest_link}<p><a href=\"archive.html\">View the report archive</a></p></body></html>\n"


def update_pages_index(docs_dir: str | Path = "docs") -> None:
    docs_path = Path(docs_dir)
    reports_dir = docs_path / "reports"
    docs_path.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_paths = list(reports_dir.glob("album-review-digest-*_to_*.html"))
    latest = max(report_paths, default=None, key=lambda p: p.name)
    (docs_path / "archive.html").write_text(_render_archive_page(report_paths, docs_path), encoding="utf-8")
    (docs_path / "index.html").write_text(_render_index_page(latest, docs_path), encoding="utf-8")


def render_report(items: list[dict], window: ReportWindow, output_dir: str | Path="docs/reports", source_statuses: list[dict] | None = None) -> Path:
    sections = build_sections(items, window, source_statuses)
    if Environment:
        env=Environment(loader=FileSystemLoader("src/report/templates"), autoescape=select_autoescape())
        try:
            html=env.get_template("weekly_digest.html.j2").render(window=window, **sections)
        except Exception:
            html=_fallback_html(items, window, source_statuses)
    else:
        html=_fallback_html(items, window, source_statuses)
    out=Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    path=out / f"album-review-digest-{window.start}_to_{window.end}.html"
    path.write_text(html, encoding="utf-8")
    if out.name == "reports" and out.parent.name == "docs":
        update_pages_index(out.parent)
    return path
