from datetime import date
from pathlib import Path
from src.models import ReviewItem
from src.report.html import render_report
from src.utils.dates import ReportWindow

def test_html_rendering_missing_scores(tmp_path):
    item = ReviewItem(artist="A", album="B", review_source="Pitchfork", score_status="no_score", review_date=date(2026,6,10)).to_dict()
    path = render_report([item], ReportWindow(date(2026,6,9), date(2026,6,15), date(2026,6,2), date(2026,6,16), "Asia/Shanghai"), tmp_path)
    assert "—/10" in path.read_text(encoding="utf-8")

def test_manual_check_creation_for_parser_failure():
    item = ReviewItem(artist="A", album="B", parse_status="parse_failed", status="manual_check", manual_check_reason="parser_error")
    assert item.status == "manual_check"

def test_docs_pages_index_updated_for_default_report_output(tmp_path):
    item = ReviewItem(artist="A", album="B", review_source="Pitchfork", normalized_score_10=8, review_date=date(2026,6,10)).to_dict()
    docs_dir = tmp_path / "docs"
    path = render_report([item], ReportWindow(date(2026,6,9), date(2026,6,15), date(2026,6,2), date(2026,6,16), "Asia/Shanghai"), docs_dir / "reports")

    assert path == docs_dir / "reports" / "album-review-digest-2026-06-09_to_2026-06-15.html"
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in (docs_dir / "index.html").read_text(encoding="utf-8")
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in (docs_dir / "archive.html").read_text(encoding="utf-8")
