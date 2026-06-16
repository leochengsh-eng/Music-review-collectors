"""Optional legacy SMTP delivery helpers.

Email is no longer the primary delivery method. The scheduled pipeline publishes
GitHub Pages via `--delivery pages`; this module is intentionally unused unless a
caller wires SMTP settings explicitly outside the default workflow.
"""
from __future__ import annotations
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def format_subject(start, end) -> str:
    return f"Album Review Weekly Digest｜{start} to {end}"


def send_email(html_path: Path, start, end, to_address: str | None = None) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587") or 587)
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_address = os.getenv("EMAIL_FROM")
    to_address = to_address or os.getenv("EMAIL_TO")
    missing = [name for name, value in {"SMTP_HOST": host, "EMAIL_FROM": from_address, "EMAIL_TO": to_address}.items() if not value]
    if missing:
        raise RuntimeError(f"Email delivery is disabled or missing settings: {', '.join(missing)}")
    html = html_path.read_text(encoding="utf-8")
    msg = EmailMessage(); msg["Subject"] = format_subject(start, end); msg["From"] = from_address; msg["To"] = to_address
    msg.set_content("Please view the HTML version of this weekly album review digest.")
    msg.add_alternative(html, subtype="html")
    msg.add_attachment(html.encode("utf-8"), maintype="text", subtype="html", filename=html_path.name)
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(msg)
