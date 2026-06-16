from pathlib import Path
from src.report.site import ReportMeta, build_static_site, discover_reports, merge_report_meta


def test_pages_site_preserves_previous_reports(tmp_path):
    reports = tmp_path / "docs" / "reports"
    reports.mkdir(parents=True)
    old = reports / "album-review-digest-2026-06-02_to_2026-06-08.html"
    old.write_text("old report", encoding="utf-8")
    new = reports / "album-review-digest-2026-06-09_to_2026-06-15.html"
    new.write_text("new report", encoding="utf-8")

    build_static_site(ReportMeta("2026-06-09", "2026-06-15", new.name, 3, 1, ("A — B",)), tmp_path / "docs")

    assert old.read_text(encoding="utf-8") == "old report"
    assert "reports/album-review-digest-2026-06-09_to_2026-06-15.html" in (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")
    archive = (tmp_path / "docs" / "archive.html").read_text(encoding="utf-8")
    assert "2026-06-09 to 2026-06-15" in archive
    assert "2026-06-02 to 2026-06-08" in archive


def test_merge_report_meta_overwrites_same_range_only():
    old = ReportMeta("2026-06-09", "2026-06-15", "album-review-digest-2026-06-09_to_2026-06-15.html", 1, 0)
    updated = ReportMeta("2026-06-09", "2026-06-15", "album-review-digest-2026-06-09_to_2026-06-15.html", 5, 2)
    merged = merge_report_meta([old], updated)
    assert len(merged) == 1
    assert merged[0].recommended_count == 5
