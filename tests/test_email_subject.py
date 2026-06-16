from src.delivery.emailer import format_subject

def test_email_subject():
    assert format_subject("2026-06-09", "2026-06-15") == "Album Review Weekly Digest｜2026-06-09 to 2026-06-15"
