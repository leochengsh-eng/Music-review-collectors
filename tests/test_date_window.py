from datetime import datetime
from zoneinfo import ZoneInfo
from src.utils.dates import previous_tuesday_window, is_late_addition

def test_weekly_date_window():
    w = previous_tuesday_window(datetime(2026,6,16,10,0,tzinfo=ZoneInfo("Asia/Shanghai")), "Asia/Shanghai", 14)
    assert str(w.start) == "2026-06-09"
    assert str(w.end) == "2026-06-15"
    assert str(w.scan_start) == "2026-06-02"

def test_late_additions_logic():
    w = previous_tuesday_window(datetime(2026,6,16,10,0,tzinfo=ZoneInfo("Asia/Shanghai")), "Asia/Shanghai", 14)
    assert is_late_addition(w.scan_start, w)
    assert not is_late_addition(w.start, w)
