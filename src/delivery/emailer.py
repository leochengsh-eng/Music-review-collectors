from __future__ import annotations
import smtplib
from email.message import EmailMessage
from pathlib import Path
from src.config import Settings

def format_subject(start, end) -> str:
    return f"Album Review Weekly Digest｜{start} to {end}"

def send_email(settings: Settings, html_path: Path, start, end) -> None:
    missing=[k for k,v in {"SMTP_HOST":settings.smtp_host,"EMAIL_FROM":settings.email_from}.items() if not v]
    if missing: raise RuntimeError(f"Missing email settings: {', '.join(missing)}")
    html=html_path.read_text(encoding="utf-8")
    msg=EmailMessage(); msg["Subject"]=format_subject(start,end); msg["From"]=settings.email_from; msg["To"]=settings.email_to
    msg.set_content("Please view the HTML version of this weekly album review digest.")
    msg.add_alternative(html, subtype="html")
    msg.add_attachment(html.encode("utf-8"), maintype="text", subtype="html", filename=html_path.name)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        if settings.smtp_username and settings.smtp_password: smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)
