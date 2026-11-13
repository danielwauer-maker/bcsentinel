"""Issue #43: one-use, identity-bound enrollment; legacy rollout unchanged."""
from __future__ import annotations

from base64 import b64encode
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.pilot_enrollment_models import PilotEnrollment, PilotEnrollmentAudit
from app.models import Tenant, TenantScanCredit


COMPANY_ID = "22222222-2222-2222-2222-222222222222"
ENTRA_ID = "11111111-1111-1111-1111-111111111111"


def _operator():
    return {"Authorization": "Basic " + b64encode(b"admin-test:admin-password-for-tests-123").decode()}


def _pilot_payload():
    return {
        "entra_tenant_id": ENTRA_ID, "environment_name": "Sandbox",
        "environment_type": "sandbox", "company_id": COMPANY_ID,
        "company_name": "Pilot GmbH",
        "contact_email": "contact@example.com",
        "authorized_email": "authorized@example.com",
        "commercial_profile": "pilot_free_entry",
    }


def _registration(token, **overrides):
    return {
        "entra_tenant_id": ENTRA_ID, "environment_name": "Sandbox",
        "environment_type": "sandbox", "company_id": COMPANY_ID,
        "company_name": "Pilot GmbH", "app_version": "1.0.2.59",
        "contact_email": "authorized@example.com",
        "invite_code": token,
        **overrides,
    }


def _approve(client, settings_state):
    settings_state(PILOT_ENROLLMENT_ENABLED=True)
    created = client.post("/internal/pilot/enrollments", json=_pilot_payload(), headers=_operator())
    assert created.status_code == 200, created.text
    assert created.json()["status"] == "PENDING"
    assert "enrollment_token_once" not in created.text
    assert "token_hash" not in created.text
    enrollment_id = created.json()["id"]
    approved = client.post(
        f"/internal/pilot/enrollments/{enrollment_id}/approve",
        json={"lifetime_hours": 2}, headers=_operator(),
    )
    assert approved.status_code == 200, approved.text
    token = approved.json()["enrollment_token_once"]
    assert token.startswith("bcs_enr_")
    return enrollment_id, token


def test_pilot_disabled_preserves_legacy_gate(client, settings_state):
    settings_state(PILOT_ENROLLMENT_ENABLED=False, TENANT_REGISTRATION_INVITE_CODE="legacy-secret")
    assert client.post("/tenant/register", json=_registration("bad-code")).status_code == 403
    assert client.get("/internal/pilot/enrollments", headers=_operator()).status_code == 404


def test_one_use_enrollment_binds_identity_without_plaintext_persistence(client, settings_state, db_session):
    enrollment_id, token = _approve(client, settings_state)
    incorrect_email = client.post("/tenant/register", json=_registration(token, contact_email="wrong@example.com"))
    assert incorrect_email.status_code == 403
    incorrect_company = client.post("/tenant/register", json=_registration(token, company_id="33333333-3333-3333-3333-333333333333"))
    assert incorrect_company.status_code == 403

    registered = client.post("/tenant/register", json=_registration(token))
    assert registered.status_code == 200, registered.text
    tenant_id = registered.json()["tenant_id"]
    assert client.post("/tenant/register", json=_registration(token)).status_code == 403
    row = db_session.get(PilotEnrollment, enrollment_id)
    db_session.refresh(row)
    assert row.status == "REGISTERED"
    assert row.registered_tenant_id == tenant_id
    assert row.token_hash is None
    assert token not in str(db_session.scalars(select(PilotEnrollmentAudit)).all())
    assert db_session.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id)) is not None
    credits = db_session.scalars(select(TenantScanCredit).where(TenantScanCredit.tenant_id == tenant_id)).all()
    assert len(credits) == 1
    status = client.get(f"/internal/pilot/enrollments/{enrollment_id}", headers=_operator())
    assert status.status_code == 200
    assert token not in status.text
    assert "token_hash" not in status.text


def test_rejected_invite_never_consumes_enrollment(client, settings_state, db_session):
    enrollment_id, token = _approve(client, settings_state)
    bad_company = client.post("/tenant/register", json=_registration(token, company_id="33333333-3333-3333-3333-333333333333"))
    assert bad_company.status_code == 403
    row = db_session.get(PilotEnrollment, enrollment_id)
    db_session.refresh(row)
    assert row.status == "APPROVED"
    assert client.post("/tenant/register", json=_registration(token)).status_code == 200


def test_expired_revoked_and_reissued_codes_fail_closed(client, settings_state, db_session):
    enrollment_id, token = _approve(client, settings_state)
    row = db_session.get(PilotEnrollment, enrollment_id)
    row.token_expires_at_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    assert client.post("/tenant/register", json=_registration(token)).status_code == 403
    reissue = client.post(f"/internal/pilot/enrollments/{enrollment_id}/approve",
                          json={"lifetime_hours": 1}, headers=_operator())
    assert reissue.status_code == 200
    second = reissue.json()["enrollment_token_once"]
    assert second != token
    assert client.post("/tenant/register", json=_registration(token)).status_code == 403
    revoke = client.post(f"/internal/pilot/enrollments/{enrollment_id}/revoke", headers=_operator())
    assert revoke.status_code == 200
    assert revoke.json()["status"] == "REVOKED"
    assert client.post("/tenant/register", json=_registration(second)).status_code == 403


def test_admin_requires_authentication(client, settings_state):
    settings_state(PILOT_ENROLLMENT_ENABLED=True)
    response = client.post("/internal/pilot/enrollments", json=_pilot_payload())
    assert response.status_code == 401
    assert client.get("/internal/pilot/enrollments").status_code == 401


def test_existing_tenant_reregistration_with_credentials_not_new_enrollment(client, settings_state):
    _, token = _approve(client, settings_state)
    first = client.post("/tenant/register", json=_registration(token))
    assert first.status_code == 200
    data = first.json()
    followup = client.post(
        "/tenant/register",
        json=_registration(None, existing_tenant_id=data["tenant_id"]),
        headers={"X-Tenant-Id": data["tenant_id"], "X-Api-Token": data["api_token"]},
    )
    assert followup.status_code == 200, followup.text
    assert followup.json()["tenant_id"] == data["tenant_id"]
