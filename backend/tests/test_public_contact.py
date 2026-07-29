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
