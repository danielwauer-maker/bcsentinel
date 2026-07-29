from __future__ import annotations

from app.core.settings import settings


def payload(**overrides):
    data = {
        "name": "Daniel Wauer",
        "email": "daniel@example.com",
        "company": "BCSentinel Test",
        "topic": "Pilot",
        "message": "Ich interessiere mich für einen betreuten BCSentinel-Pilot.",
        "locale": "de",
        "website": None,
    }
    data.update(overrides)
    return data


def test_public_contact_delivers_message(client, monkeypatch):
    delivered = []

    def fake_send(message):
        delivered.append(message)

    monkeypatch.setattr("app.routers.public.send_public_contact_message", fake_send)
    response = client.post("/public/contact", json=payload())

    assert response.status_code == 202
    assert response.json()["accepted"] is True
    assert delivered[0].email == "daniel@example.com"
    assert delivered[0].topic == "Pilot"


def test_public_contact_honeypot_is_accepted_without_delivery(client, monkeypatch):
    def fail_send(_message):
        raise AssertionError("honeypot message must not be delivered")

    monkeypatch.setattr("app.routers.public.send_public_contact_message", fail_send)
    response = client.post("/public/contact", json=payload(website="spam.example"))

    assert response.status_code == 202
    assert response.json()["accepted"] is True


def test_public_contact_rejects_invalid_payload(client):
    response = client.post("/public/contact", json=payload(email="invalid", message="short"))
    assert response.status_code == 422


def test_public_contact_rejects_link_spam(client):
    response = client.post(
        "/public/contact",
        json=payload(message="Links https://a.example https://b.example https://c.example"),
    )
    assert response.status_code == 422


def test_public_contact_rate_limit(client, monkeypatch):
    monkeypatch.setattr("app.routers.public.send_public_contact_message", lambda _message: None)
    monkeypatch.setattr(settings, "CONTACT_RATE_LIMIT_ATTEMPTS", 1)
    monkeypatch.setattr(settings, "CONTACT_RATE_LIMIT_WINDOW_SECONDS", 600)

    assert client.post("/public/contact", json=payload()).status_code == 202
    response = client.post("/public/contact", json=payload(email="other@example.com"))
    assert response.status_code == 429


def test_public_contact_returns_503_when_delivery_is_unconfigured(client, monkeypatch):
    from app.services.public_contact_service import ContactDeliveryUnavailable

    def unavailable(_message):
        raise ContactDeliveryUnavailable("not configured")

    monkeypatch.setattr("app.routers.public.send_public_contact_message", unavailable)
    response = client.post("/public/contact", json=payload())
    assert response.status_code == 503


def test_public_contact_service_uses_server_side_smtp_and_reply_to(monkeypatch):
    from app.services.public_contact_service import PublicContactMessage, send_public_contact_message

    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["connection"] = (host, port, timeout)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            sent["tls"] = True

        def login(self, username, password):
            sent["login"] = (username, password)

        def send_message(self, message, from_addr, to_addrs):
            sent["message"] = message
            sent["from_addr"] = from_addr
            sent["to_addrs"] = to_addrs

    monkeypatch.setattr("app.services.public_contact_service.smtplib.SMTP", FakeSMTP)
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp-relay.brevo.com")
    monkeypatch.setattr(settings, "SMTP_PORT", 587)
    monkeypatch.setattr(settings, "SMTP_USERNAME", "brevo-user")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "brevo-secret")
    monkeypatch.setattr(settings, "SMTP_USE_TLS", True)
    monkeypatch.setattr(settings, "SMTP_FROM_EMAIL", "noreply@bcsentinel.com")
    monkeypatch.setattr(settings, "SMTP_FROM_NAME", "BCSentinel")
    monkeypatch.setattr(settings, "CONTACT_RECIPIENT_EMAIL", "support@bcsentinel.com")

    send_public_contact_message(
        PublicContactMessage(
            name="Daniel Wauer",
            email="daniel@example.com",
            company="BCSentinel Test",
            topic="Pilot",
            message="Bitte senden Sie mir Informationen zum Pilotprogramm.",
            locale="de",
            request_id="req-test",
        )
    )

    assert sent["connection"] == ("smtp-relay.brevo.com", 587, 15)
    assert sent["tls"] is True
    assert sent["login"] == ("brevo-user", "brevo-secret")
    assert sent["message"]["Reply-To"] == "daniel@example.com"
    assert sent["from_addr"] == "noreply@bcsentinel.com"
    assert sent["to_addrs"] == ["support@bcsentinel.com"]
