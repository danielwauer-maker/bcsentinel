from __future__ import annotations

import html
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.observability import log_event
from app.core.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PublicContactMessage:
    name: str
    email: str
    company: str | None
    topic: str
    message: str
    locale: str
    request_id: str | None


class ContactDeliveryUnavailable(RuntimeError):
    pass


class ContactDeliveryFailed(RuntimeError):
    pass


def _clean_header(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())


def _render_html(payload: PublicContactMessage) -> str:
    rows = [
        ("Name", payload.name),
        ("Email", payload.email),
        ("Unternehmen / Company", payload.company or "—"),
        ("Thema / Topic", payload.topic),
        ("Sprache / Locale", payload.locale),
        ("Request ID", payload.request_id or "—"),
    ]
    details = "".join(
        f"<tr><th style='text-align:left;padding:6px 12px 6px 0'>{html.escape(label)}</th>"
        f"<td style='padding:6px 0'>{html.escape(value)}</td></tr>"
        for label, value in rows
    )
    body = html.escape(payload.message).replace("\n", "<br>")
    return (
        "<h2>Neue BCSentinel-Kontaktanfrage</h2>"
        f"<table>{details}</table>"
        "<h3>Nachricht</h3>"
        f"<p>{body}</p>"
        "<hr><p style='color:#667085;font-size:12px'>"
        "Übermittelt über den eigenen BCSentinel-Kontakt-Endpunkt."
        "</p>"
    )


def send_public_contact_message(payload: PublicContactMessage) -> None:
    host = (settings.SMTP_HOST or "").strip()
    from_email = (settings.SMTP_FROM_EMAIL or "").strip()
    recipient = (settings.CONTACT_RECIPIENT_EMAIL or "").strip()
    if not host or not from_email or not recipient:
        raise ContactDeliveryUnavailable("Contact email delivery is not configured.")

    subject = _clean_header(f"BCSentinel Kontakt: {payload.topic} – {payload.name}")[:180]
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = (
        f"{_clean_header(settings.SMTP_FROM_NAME)} <{from_email}>"
        if settings.SMTP_FROM_NAME
        else from_email
    )
    message["To"] = recipient
    message["Reply-To"] = _clean_header(payload.email)
    message.set_content(
        "Neue BCSentinel-Kontaktanfrage\n\n"
        f"Name: {payload.name}\n"
        f"Email: {payload.email}\n"
        f"Unternehmen: {payload.company or '—'}\n"
        f"Thema: {payload.topic}\n"
        f"Sprache: {payload.locale}\n"
        f"Request ID: {payload.request_id or '—'}\n\n"
        f"{payload.message}\n"
    )
    message.add_alternative(_render_html(payload), subtype="html")

    try:
        with smtplib.SMTP(host, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            username = (settings.SMTP_USERNAME or "").strip()
            password = settings.SMTP_PASSWORD or ""
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message, from_addr=from_email, to_addrs=[recipient])
    except Exception as exc:  # pragma: no cover - provider/network specifics
        log_event(
            logger,
            logging.ERROR,
            "public_contact_delivery_failed",
            "Public contact email delivery failed.",
            request_id=payload.request_id,
            error_type=type(exc).__name__,
        )
        raise ContactDeliveryFailed("Contact email delivery failed.") from exc

    log_event(
        logger,
        logging.INFO,
        "public_contact_delivered",
        "Public contact email delivered.",
        request_id=payload.request_id,
        topic=payload.topic,
        locale=payload.locale,
    )
