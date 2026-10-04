from __future__ import annotations

from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import DashboardUser, PublicContactMessage, Tenant
from app.services import dashboard_invite_service as invites
from app.services.email_template_service import DEFAULT_ADMIN_EMAIL_TEMPLATES, ensure_default_email_templates


def test_public_contact_is_persisted_even_when_mail_transport_is_unavailable(client, monkeypatch) -> None:
    import app.routers.public as public_router

    monkeypatch.setattr(public_router, "_send_html_email", lambda **kwargs: (False, "temporary provider failure"))

    response = client.post(
        "/public/contact",
        json={
            "first_name": "Pilot",
            "last_name": "Customer",
            "company": "Example GmbH",
            "email": "pilot@example.test",
            "message": "We would like to join the BCSentinel Core pilot.",
            "intent": "pilot",
            "language": "en",
            "privacy_accepted": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["delivery_status"] == "stored"

    with SessionLocal() as db:
        row = db.get(PublicContactMessage, body["message_id"])
        assert row is not None
        assert row.email == "pilot@example.test"
        assert row.intent == "pilot"
        assert row.privacy_accepted is True
        assert row.mail_status == "stored"


def test_public_contact_requires_privacy_acknowledgement(client) -> None:
    response = client.post(
        "/public/contact",
        json={
            "email": "pilot@example.test",
            "message": "A sufficiently long pilot request.",
            "privacy_accepted": False,
        },
    )
    assert response.status_code == 422


def test_dashboard_welcome_templates_exist_in_both_languages() -> None:
    assert "dashboard_welcome_de" in DEFAULT_ADMIN_EMAIL_TEMPLATES
    assert "dashboard_welcome_en" in DEFAULT_ADMIN_EMAIL_TEMPLATES
    assert "dashboard_url" in DEFAULT_ADMIN_EMAIL_TEMPLATES["dashboard_welcome_de"]["placeholders"]
    assert "support_email" in DEFAULT_ADMIN_EMAIL_TEMPLATES["dashboard_welcome_en"]["placeholders"]


def test_dashboard_welcome_uses_tenant_language_and_real_dashboard_url(tenant_factory, monkeypatch) -> None:
    tenant_info = tenant_factory(tenant_id="welcome_tenant")
    captured: dict[str, str] = {}

    def fake_send(*, target_email: str, subject: str, html_body: str):
        captured["target_email"] = target_email
        captured["subject"] = subject
        captured["html_body"] = html_body
        return True, None

    monkeypatch.setattr(invites, "_send_html_email", fake_send)

    with SessionLocal() as db:
        tenant = db.query(Tenant).filter_by(tenant_id=tenant_info["tenant_id"]).one()
        tenant.preferred_language = "de"
        user = DashboardUser(
            email="welcome@example.test",
            normalized_email="welcome@example.test",
            status="active",
            must_change_password=False,
            password_hash="hash",
            created_at_utc=datetime.now(timezone.utc),
            updated_at_utc=datetime.now(timezone.utc),
            invite_mail_status="sent",
        )
        db.add(user)
        db.flush()
        ensure_default_email_templates(db)
        sent, error = invites.send_dashboard_welcome(db, user=user, tenant=tenant)

    assert sent is True
    assert error is None
    assert captured["target_email"] == "welcome@example.test"
    assert "Willkommen" in captured["subject"]
    assert "/dashboard" in captured["html_body"]


def test_operator_contact_inbox_is_admin_protected_and_renderable(client) -> None:
    unauthenticated = client.get("/admin/contact-inbox")
    assert unauthenticated.status_code == 401

    authenticated = client.get(
        "/admin/contact-inbox",
        auth=("admin-test", "admin-password-for-tests-123"),
    )
    assert authenticated.status_code == 200
    assert "Contact Inbox" in authenticated.text
