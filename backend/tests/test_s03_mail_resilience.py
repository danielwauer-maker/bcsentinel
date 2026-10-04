from __future__ import annotations

import smtplib

from app.core.settings import settings
from app.services import dashboard_invite_service as invites


class _TransientThenSuccessSMTP:
    attempts = 0

    def __init__(self, *args, **kwargs):
        type(self).attempts += 1
        if type(self).attempts < 3:
            raise smtplib.SMTPServerDisconnected("temporary")
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def starttls(self):
        return None
    def login(self, username, password):
        return None
    def sendmail(self, from_email, recipients, payload):
        return {}


class _PermanentSMTP:
    attempts = 0

    def __init__(self, *args, **kwargs):
        type(self).attempts += 1
        raise smtplib.SMTPResponseException(550, b"rejected")


def _configure(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.example.test")
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "noreply@example.test")
    monkeypatch.setattr(settings, "SMTP_FROM_NAME", "BCSentinel")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USE_TLS", True)
    monkeypatch.setattr(settings, "SMTP_USERNAME", "")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "")


def test_transient_smtp_failure_is_retried_and_recovers(monkeypatch) -> None:
    _configure(monkeypatch)
    _TransientThenSuccessSMTP.attempts = 0
    monkeypatch.setattr(invites.smtplib, "SMTP", _TransientThenSuccessSMTP)

    sent, error = invites._send_html_email(
        target_email="pilot@example.test",
        subject="Invite",
        html_body="<p>hello</p>",
    )

    assert sent is True
    assert error is None
    assert _TransientThenSuccessSMTP.attempts == 3


def test_permanent_smtp_failure_is_not_retried_and_is_safely_classified(monkeypatch) -> None:
    _configure(monkeypatch)
    _PermanentSMTP.attempts = 0
    monkeypatch.setattr(invites.smtplib, "SMTP", _PermanentSMTP)

    sent, error = invites._send_html_email(
        target_email="pilot@example.test",
        subject="Invite",
        html_body="<p>hello</p>",
    )

    assert sent is False
    assert _PermanentSMTP.attempts == 1
    assert error == "SMTP permanent failure (550) after 1 attempt(s)."
    assert "rejected" not in error
