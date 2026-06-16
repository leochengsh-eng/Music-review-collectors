from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from datetime import datetime, date
from src.config import load_settings, load_sources
from src.collector.rss import collect_rss
from src.collector.webpage import collect_webpage
from src.collector.aggregator import collect_aggregator
from src.delivery.emailer import send_email
from src.models import ReviewItem
from src.normalize.genres import classify_genre
from src.normalize.scores import is_recommendation
from src.report.html import render_report
from src.storage.db import connect, upsert_reviews, insert_source_statuses, load_reviews
from src.utils.dates import previous_tuesday_window, ReportWindow
from src.utils.logging import configure_logging

def enrich(items: list[ReviewItem]) -> list[ReviewItem]:
    now=datetime.utcnow()
    for item in items:
        item.first_seen_at=item.first_seen_at or now; item.last_seen_at=now
        bucket, sub, conf, excluded = classify_genre(item.subgenre)
        item.genre_bucket=bucket; item.genre_confidence=conf; item.excluded_reason=excluded
        if excluded: item.status="excluded"
        elif item.parse_status != "success": item.status="manual_check"
        elif item.normalized_score_10 is not None and is_recommendation(item.normalized_score_10): item.reason_for_inclusion="high_score"
        if item.release_type == "unknown":
            item.status="manual_check"; item.manual_check_reason=item.manual_check_reason or "unknown_release_type"
    return items

def export_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields=["artist","album","release_type","review_source","review_url","review_date","raw_score","normalized_score_10","genre_bucket","subgenre","status","manual_check_reason"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows([{k:r.get(k) for k in fields} for r in rows])

MVP_SOURCE_IDS = {"pitchfork", "guardian", "album_of_the_year", "metacritic"}

def run_collection(window):
    all_items=[]; statuses=[]
    sources = [s for s in load_sources() if s.get("id") in MVP_SOURCE_IDS]
    sources.sort(key=lambda s: (0 if s.get("id") in {"pitchfork", "guardian"} else 1, s.get("name", "")))
    for source in sources:
        if not source.get("enabled", True): continue
        if source.get("type") == "rss": items,status=collect_rss(source)
        elif source.get("type") == "aggregator": items,status=collect_aggregator(source)
        else: items,status=collect_webpage(source)
        all_items.extend(items); statuses.append(status)
    return enrich(all_items), statuses

def pipeline(mode, window, send=False):
    logger=configure_logging(Path(f"logs/run-{window.end}.log")); conn=connect()
    if mode == "report-only": items=[]; statuses=[]
    else: items,statuses=run_collection(window); upsert_reviews(conn, items); insert_source_statuses(conn, statuses)
    rows=load_reviews(conn)
    html_path=render_report(rows, window, source_statuses=[s.__dict__ for s in statuses])
    export_csv(Path(f"outputs/csv/reviews-{window.start}_to_{window.end}.csv"), rows)
    export_csv(Path(f"outputs/csv/recommended-{window.start}_to_{window.end}.csv"), [r for r in rows if (r.get('normalized_score_10') or 0)>=7])
    export_csv(Path(f"outputs/csv/manual-check-{window.start}_to_{window.end}.csv"), [r for r in rows if r.get('status')=='manual_check'])
    summary={"start":str(window.start),"end":str(window.end),"html":str(html_path),"source_statuses":[s.__dict__ for s in statuses],"total_reviews":len(rows)}
    out=Path(f"outputs/json/run-summary-{window.start}_to_{window.end}.json"); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(summary, default=str, ensure_ascii=False, indent=2), encoding="utf-8")
    if send:
        try: send_email(load_settings(), html_path, window.start, window.end)
        except Exception as exc: logger.error("Email delivery failed; artifacts preserved: %s", exc)
    return html_path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode", choices=["weekly","backfill","report-only","test-email"], required=True); p.add_argument("--lookback-days", type=int); p.add_argument("--start-date"); p.add_argument("--end-date")
    args=p.parse_args(); settings=load_settings(); lookback=args.lookback_days or settings.report_lookback_days
    if args.start_date and args.end_date: window=ReportWindow(date.fromisoformat(args.start_date), date.fromisoformat(args.end_date), date.fromisoformat(args.start_date), date.fromisoformat(args.end_date), settings.report_timezone)
    else: window=previous_tuesday_window(tz_name=settings.report_timezone, lookback_days=lookback)
    email_requested = args.mode == "test-email" or (args.mode == "weekly" and settings.email_enabled)
    pipeline("weekly" if args.mode=="test-email" else args.mode, window, send=email_requested)
if __name__ == "__main__": main()
