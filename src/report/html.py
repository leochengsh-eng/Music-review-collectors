from __future__ import annotations
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ModuleNotFoundError:
    Environment = FileSystemLoader = select_autoescape = None
from src.utils.dates import ReportWindow, in_formal_window, is_late_addition

def build_sections(items: list[dict], window: ReportWindow):
    recommended=[i for i in items if (i.get('normalized_score_10') or 0) >= 7 and i.get('status') != 'manual_check']
    by_genre={g: [] for g in ["Pop","Rock","Electronic","R&B / Soul","Folk / Country","Global / C-Pop","Unknown"]}
    for i in recommended: by_genre.setdefault(i.get('genre_bucket') or 'Unknown', []).append(i)
    manual=[i for i in items if i.get('status')=='manual_check' or i.get('parse_status')!='success' or i.get('dedupe_status')=='uncertain']
    aggregators=[i for i in items if i.get('status')=='aggregator_find']
    late=[i for i in items if is_late_addition(__import__('datetime').date.fromisoformat(i['review_date']) if i.get('review_date') else None, window)]
    new=[i for i in items if in_formal_window(__import__('datetime').date.fromisoformat(i['review_date']) if i.get('review_date') else window.start, window)]
    return {"recommended": recommended, "by_genre": by_genre, "manual": manual, "aggregators": aggregators, "late": late, "new": new}

def render_report(items: list[dict], window: ReportWindow, output_dir: str | Path="outputs/html") -> Path:
    sections = build_sections(items, window)
    if Environment:
        env=Environment(loader=FileSystemLoader("src/report/templates"), autoescape=select_autoescape())
        html=env.get_template("weekly_digest.html.j2").render(window=window, **sections)
    else:
        cards = "".join(f"<div class=\"card\"><b>{i.get('artist')} — {i.get('album')}</b><span>{i.get('normalized_score_10') if i.get('normalized_score_10') is not None else '—'}/10</span></div>" for i in items)
        html=f"<!doctype html><html><body><h1>Album Review Weekly Digest</h1><p>{window.start} to {window.end}</p>{cards}</body></html>"
    out=Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    path=out / f"album-review-digest-{window.start}_to_{window.end}.html"
    path.write_text(html, encoding="utf-8")
    return path
