from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

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
