from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

REPORT_RE = re.compile(r"album-review-digest-(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})\.html$")


@dataclass(frozen=True)
class ReportMeta:
    start: str
    end: str
    filename: str
    recommended_count: int = 0
    manual_count: int = 0
    highlights: tuple[str, ...] = ()

    @property
    def href(self) -> str:
        return f"reports/{self.filename}"


def report_filename(start, end) -> str:
    return f"album-review-digest-{start}_to_{end}.html"


def discover_reports(reports_dir: str | Path = "docs/reports") -> list[ReportMeta]:
    root = Path(reports_dir)
    reports: list[ReportMeta] = []
    if not root.exists():
        return reports
    for path in root.glob("album-review-digest-*_to_*.html"):
        match = REPORT_RE.match(path.name)
        if match:
            reports.append(ReportMeta(start=match.group(1), end=match.group(2), filename=path.name))
    return sorted(reports, key=lambda r: (r.start, r.end), reverse=True)


def merge_report_meta(existing: Iterable[ReportMeta], current: ReportMeta) -> list[ReportMeta]:
    by_name = {r.filename: r for r in existing}
    by_name[current.filename] = current
    return sorted(by_name.values(), key=lambda r: (r.start, r.end), reverse=True)


def _page_shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
    body{{margin:0;background:#f6f3ef;color:#241f1b;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}}
    .wrap{{max-width:980px;margin:auto;padding:32px 16px;}}
    .hero{{background:#fff;border:1px solid #e8ded3;border-radius:24px;padding:28px;box-shadow:0 12px 30px #0000000a;}}
    h1{{margin:0 0 8px;font-size:34px;}} h2{{margin-top:30px;}}
    .sub,.meta{{color:#756b62;}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-top:16px;}}
    .card{{background:#fff;border:1px solid #e8ded3;border-radius:18px;padding:18px;box-shadow:0 6px 18px #0000000a;}}
    .button{{display:inline-block;background:#151515;color:#fff;text-decoration:none;border-radius:999px;padding:10px 16px;font-weight:700;margin-top:12px;}}
    a{{color:#8d3b22;}} .pill{{display:inline-block;background:#efe7dc;border-radius:999px;padding:4px 9px;margin:3px;font-size:13px;}}
    .topnav{{margin-bottom:18px;}} .topnav a{{margin-right:12px;}}
    @media(max-width:600px){{.wrap{{padding:20px 12px;}} h1{{font-size:28px;}} .hero{{padding:20px;}}}}
  </style>
</head>
<body><main class=\"wrap\">{body}</main></body></html>"""


def write_index(docs_dir: str | Path, latest: ReportMeta | None) -> Path:
    docs = Path(docs_dir); docs.mkdir(parents=True, exist_ok=True)
    if latest:
        highlights = "".join(f"<li>{h}</li>" for h in latest.highlights) or "<li>No highlights available yet.</li>"
        body = f"""
        <nav class=\"topnav\"><a href=\"archive.html\">Archive</a></nav>
        <section class=\"hero\"><h1>Album Review Weekly Digest</h1><p class=\"sub\">Latest report: {latest.start} to {latest.end}</p>
        <p><span class=\"pill\">Recommended: {latest.recommended_count}</span><span class=\"pill\">Manual Check: {latest.manual_count}</span></p>
        <a class=\"button\" href=\"{latest.href}\">Open latest report</a></section>
        <h2>This week’s Highlights</h2><div class=\"card\"><ul>{highlights}</ul></div>
        <p><a href=\"archive.html\">View all archived reports</a></p>
        """
    else:
        body = "<section class=\"hero\"><h1>Album Review Weekly Digest</h1><p class=\"sub\">No reports generated yet.</p></section><p><a href=\"archive.html\">Archive</a></p>"
    path = docs / "index.html"
    path.write_text(_page_shell("Album Review Weekly Digest", body), encoding="utf-8")
    return path


def write_archive(docs_dir: str | Path, reports: list[ReportMeta]) -> Path:
    docs = Path(docs_dir); docs.mkdir(parents=True, exist_ok=True)
    cards = "".join(
        f"<article class=\"card\"><h2>{r.start} to {r.end}</h2><p><span class=\"pill\">Recommended: {r.recommended_count}</span><span class=\"pill\">Manual Check: {r.manual_count}</span></p><a class=\"button\" href=\"{r.href}\">Open report</a></article>"
        for r in reports
    ) or "<p class=\"sub\">No reports generated yet.</p>"
    body = f"<nav class=\"topnav\"><a href=\"index.html\">Home</a></nav><section class=\"hero\"><h1>Archive</h1><p class=\"sub\">All Album Review Weekly Digest reports, newest first.</p></section><div class=\"grid\">{cards}</div>"
    path = docs / "archive.html"
    path.write_text(_page_shell("Album Review Weekly Digest Archive", body), encoding="utf-8")
    return path


def build_static_site(current: ReportMeta | None = None, docs_dir: str | Path = "docs") -> list[Path]:
    docs = Path(docs_dir); reports_dir = docs / "reports"; reports_dir.mkdir(parents=True, exist_ok=True)
    reports = discover_reports(reports_dir)
    if current:
        reports = merge_report_meta(reports, current)
    latest = reports[0] if reports else None
    return [write_index(docs, latest), write_archive(docs, reports)]
