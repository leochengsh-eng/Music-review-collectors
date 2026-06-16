from datetime import date
from pathlib import Path

import yaml

from src.models import ReviewItem
from src.report.html import render_report
from src.utils.dates import ReportWindow


def window(start=date(2026, 6, 9), end=date(2026, 6, 15)):
    return ReportWindow(start, end, start, end, "Asia/Shanghai")


def test_weekly_report_preserves_previous_reports_and_archive_lists_all(tmp_path):
    docs = tmp_path / "docs"
    previous = docs / "reports" / "album-review-digest-2026-06-02_to_2026-06-08.html"
    previous.parent.mkdir(parents=True)
    previous.write_text("previous report", encoding="utf-8")

    item = ReviewItem(artist="A", album="B", review_source="Pitchfork", review_date=date(2026, 6, 10)).to_dict()
    latest = render_report([item], window(), docs / "reports")

    assert previous.exists()
    assert latest == docs / "reports" / "album-review-digest-2026-06-09_to_2026-06-15.html"
    archive = (docs / "archive.html").read_text(encoding="utf-8")
    assert "reports/album-review-digest-2026-06-02_to_2026-06-08.html" in archive
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in archive
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in (docs / "index.html").read_text(encoding="utf-8")


def test_no_demo_data_in_empty_production_report_and_failures_rendered(tmp_path):
    statuses = [{"source_name": "Metacritic", "status": "blocked", "items_found": 0, "items_parsed": 0, "items_failed": 1, "error_message": "HTTP 403 blocked"}]
    manual = ReviewItem(
        artist="Unknown Artist",
        album="Manual review required",
        review_source="Metacritic",
        review_url="https://www.metacritic.com/browse/albums/release-date/new-releases/date",
        status="manual_check",
        parse_status="parse_failed",
        manual_check_reason="HTTP 403 blocked",
    ).to_dict()

    path = render_report([manual], window(), tmp_path / "docs" / "reports", source_statuses=statuses)
    html = path.read_text(encoding="utf-8")

    assert "No valid real album data collected" in html
    assert "Manual Check" in html
    assert "Source Status" in html
    assert "HTTP 403 blocked" in html
    assert "Demo Artist" not in html
    assert "Sample Album" not in html
    assert "资料有限" not in html


def test_workflow_permissions_allow_committing_generated_reports():
    workflow = yaml.safe_load(Path(".github/workflows/weekly-digest.yml").read_text(encoding="utf-8"))

    assert workflow["permissions"]["contents"] == "write"
    text = Path(".github/workflows/weekly-digest.yml").read_text(encoding="utf-8")
    assert "git add docs outputs/csv outputs/json logs" in text
    assert "actions/upload-pages-artifact" in text
    assert "actions/deploy-pages" in text
