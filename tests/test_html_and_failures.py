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

def test_report_preserves_previous_reports_and_archive_links_all(tmp_path):
    docs_dir = tmp_path / "docs"
    old = docs_dir / "reports" / "album-review-digest-2026-06-02_to_2026-06-08.html"
    old.parent.mkdir(parents=True)
    old.write_text("old report", encoding="utf-8")

    item = ReviewItem(artist="A", album="B", review_source="Pitchfork", normalized_score_10=8, review_date=date(2026,6,10)).to_dict()
    render_report([item], ReportWindow(date(2026,6,9), date(2026,6,15), date(2026,6,2), date(2026,6,16), "Asia/Shanghai"), docs_dir / "reports")

    assert old.read_text(encoding="utf-8") == "old report"
    archive = (docs_dir / "archive.html").read_text(encoding="utf-8")
    assert "reports/album-review-digest-2026-06-02_to_2026-06-08.html" in archive
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in archive


def test_failed_collection_statuses_render_manual_check_and_source_status(tmp_path):
    window = ReportWindow(date(2026,6,9), date(2026,6,15), date(2026,6,2), date(2026,6,16), "Asia/Shanghai")
    item = ReviewItem(artist="Manual Check", album="Pitchfork source status", review_source="Pitchfork", review_url="https://pitchfork.com/rss/reviews/albums/", status="manual_check", parse_status="source_status", manual_check_reason="HTTP 503").to_dict()
    path = render_report([item], window, tmp_path / "docs" / "reports", source_statuses=[{"source_name":"Pitchfork","status":"failed","items_found":0,"items_parsed":0,"items_failed":1,"error_message":"HTTP 503"}])
    html = path.read_text(encoding="utf-8")

    assert "No valid albums were collected for this report period" in html
    assert "Manual Check" in html
    assert "Source Status" in html
    assert "HTTP 503" in html


def test_workflow_persists_generated_site_files_and_uses_write_permission():
    workflow = Path(".github/workflows/weekly-digest.yml").read_text(encoding="utf-8")

    assert "contents: write" in workflow
    assert "git add docs outputs/csv outputs/json logs" in workflow
    assert "git commit -m \"Update weekly album review digest\" || echo \"No changes to commit\"" in workflow
    assert "git push" in workflow
