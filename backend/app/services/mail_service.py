from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText
from html import escape

from app.core.settings import settings

logger = logging.getLogger(__name__)


def send_html_email(*, to_email: str, subject: str, html_body: str) -> tuple[bool, str | None]:
    host = (settings.SMTP_HOST or "").strip()
    from_email = (settings.SMTP_FROM_EMAIL or "").strip()
    target = (to_email or "").strip()

    if not host or not from_email:
        message = "SMTP not configured."
        logger.warning("SMTP not configured. Email skipped for: %s", target)
        return False, message
    if not target:
        message = "Recipient email is empty."
        logger.warning(message)
        return False, message

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = (
        f"{settings.SMTP_FROM_NAME} <{from_email}>"
        if settings.SMTP_FROM_NAME
        else from_email
    )
    msg["To"] = target

    try:
        with smtplib.SMTP(host, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            username = (settings.SMTP_USERNAME or "").strip()
            password = settings.SMTP_PASSWORD or ""
            if username:
                smtp.login(username, password)
            smtp.sendmail(from_email, [target], msg.as_string())
        return True, None
    except Exception as exc:
        logger.exception("Failed to send email to %s", target)
        return False, str(exc)


def send_waitlist_admin_notification(
    *,
    reference: str,
    contact_name: str,
    contact_email: str,
    source_page: str,
    created_at_utc: str,
) -> tuple[bool, str | None]:
    recipient = (settings.WAITLIST_ADMIN_EMAIL or "admin@bcsentinel.com").strip()
    subject = f"Neue BCSentinel-Wartelisten-Anmeldung – {reference}"
    html_body = f"""
<html>
  <body style="font-family:Arial,sans-serif;color:#14213D;line-height:1.5">
    <h2>Neue BCSentinel-Wartelisten-Anmeldung</h2>
    <p><strong>Referenz:</strong> {escape(reference)}</p>
    <p><strong>Name:</strong> {escape(contact_name)}</p>
    <p><strong>E-Mail:</strong> <a href="mailto:{escape(contact_email)}">{escape(contact_email)}</a></p>
    <p><strong>Quelle:</strong> {escape(source_page)}</p>
    <p><strong>Zeitpunkt (UTC):</strong> {escape(created_at_utc)}</p>
  </body>
</html>
""".strip()
    return send_html_email(to_email=recipient, subject=subject, html_body=html_body)
