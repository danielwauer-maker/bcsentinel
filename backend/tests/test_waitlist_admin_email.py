from app.core.settings import settings
from app.services.mail_service import send_waitlist_admin_notification


def test_waitlist_admin_notification_uses_configured_recipient(monkeypatch):
    captured = {}

    def fake_send_html_email(*, to_email: str, subject: str, html_body: str):
        captured["to_email"] = to_email
        captured["subject"] = subject
        captured["html_body"] = html_body
        return True, None

    monkeypatch.setattr("app.services.mail_service.send_html_email", fake_send_html_email)
    monkeypatch.setattr(settings, "WAITLIST_ADMIN_EMAIL", "admin@bcsentinel.com")

    sent, error = send_waitlist_admin_notification(
        reference="PILOT-000123",
        contact_name="Max Mustermann",
        contact_email="max@example.com",
        source_page="waitlist",
        created_at_utc="2026-10-27T16:00:00+00:00",
    )

    assert sent is True
    assert error is None
    assert captured["to_email"] == "admin@bcsentinel.com"
    assert "PILOT-000123" in captured["subject"]
    assert "Max Mustermann" in captured["html_body"]
    assert "max@example.com" in captured["html_body"]
