from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox, TenantLifecycleProfile
from app.models import ScanRunStatus, TenantProductEntitlement, TenantScanCredit
from app.services.lifecycle_discovery_service import discover_scan_lifecycle_events
from app.services.lifecycle_email_service import (
    EVENT_ASSESSMENT_ACTIVATED,
    EVENT_ASSESSMENT_EXPIRING,
    EVENT_ASSESSMENT_EXPIRED,
    EVENT_REGISTRATION_COMPLETED,
    EVENT_SCAN_COMPLETED,
    EVENT_SCAN_STARTED,
    EVENT_VALIDATION_EXPIRING,
    schedule_entitlement_lifecycle,
)
from app.services.lifecycle_worker_service import process_due_outbox_safely
from app.services.product_license_service import PRODUCT_ASSESSMENT, PRODUCT_VALIDATION_CHECK


def test_lifecycle_profile_requires_tenant_auth_and_queues_registration_once(
    client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    payload = {"primary_notification_email": "Owner@Example.com", "preferred_language": "de"}

    unauth = client.put("/tenant/lifecycle-profile", json=payload)
    assert unauth.status_code in {401, 422}

    headers = auth_header_factory(tenant)
    first = client.put("/tenant/lifecycle-profile", headers=headers, json=payload)
    second = client.put("/tenant/lifecycle-profile", headers=headers, json=payload)
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["primary_notification_email"] == "owner@example.com"
    assert first.json()["preferred_language"] == "de"

    with SessionLocal() as db:
        profile = db.get(TenantLifecycleProfile, tenant["tenant_id"])
        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_REGISTRATION_COMPLETED,
        ).all()
        assert profile is not None
        assert len(rows) == 1


def test_invalid_lifecycle_email_is_rejected(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    response = client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "not-an-email", "preferred_language": "en"},
    )
    assert response.status_code == 422


def test_completed_scan_is_discovered_idempotently(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "scan@example.com", "preferred_language": "en"},
    )
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="f3-scan-complete")
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            ScanRunStatus(
                run_id="f3-scan-complete",
                tenant_id=tenant["tenant_id"],
                scan_mode="deep",
                status="completed",
                progress_percent=100,
                updated_at_utc=now,
                completed_at_utc=now,
                total_modules=10,
                completed_modules=10,
                failed_modules=0,
            )
        )
        db.commit()

    with SessionLocal() as db:
        discover_scan_lifecycle_events(db)
        discover_scan_lifecycle_events(db)
        db.commit()
        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_SCAN_COMPLETED,
        ).all()
        assert len(rows) == 1
        assert "f3-scan-complete" in rows[0].payload_json


def test_running_scan_queues_started_once(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "started@example.com", "preferred_language": "de"},
    )
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            ScanRunStatus(
                run_id="f3-scan-running",
                tenant_id=tenant["tenant_id"],
                scan_mode="deep",
                status="running",
                progress_percent=10,
                updated_at_utc=now,
                started_at_utc=now,
                total_modules=10,
                completed_modules=1,
                failed_modules=0,
            )
        )
        db.commit()
    with SessionLocal() as db:
        discover_scan_lifecycle_events(db)
        discover_scan_lifecycle_events(db)
        db.commit()
        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_SCAN_STARTED,
        ).all()
        assert len(rows) == 1


def test_outbox_delivery_marks_sent_with_production_worker(
    monkeypatch, client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "mail@example.com", "preferred_language": "de"},
    )
    sent = []

    def fake_send(**kwargs):
        sent.append(kwargs)

    monkeypatch.setattr("app.services.lifecycle_worker_service._send_html_email", fake_send)
    with SessionLocal() as db:
        result = process_due_outbox_safely(db)
        db.commit()
        assert result["sent"] >= 1
        row = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_REGISTRATION_COMPLETED,
        ).one()
        assert row.status == "sent"
        assert row.attempts == 1
        assert row.sent_at_utc is not None
    assert sent
    assert sent[0]["target_email"] == "mail@example.com"


def test_stale_sending_claim_is_recovered_and_delivered(
    monkeypatch, client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "recover@example.com", "preferred_language": "en"},
    )
    with SessionLocal() as db:
        row = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_REGISTRATION_COMPLETED,
        ).one()
        row.status = "sending"
        row.attempts = 1
        row.updated_at_utc = datetime.now(timezone.utc) - timedelta(minutes=30)
        db.commit()

    monkeypatch.setattr("app.services.lifecycle_worker_service._send_html_email", lambda **kwargs: None)
    with SessionLocal() as db:
        result = process_due_outbox_safely(db)
        db.commit()
        row = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_REGISTRATION_COMPLETED,
        ).one()
        assert result["recovered"] == 1
        assert row.status == "sent"
        assert row.attempts == 2


def test_assessment_lifecycle_schedules_activation_warning_and_expiry(
    client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "assessment@example.com", "preferred_language": "en"},
    )
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        entitlement = TenantProductEntitlement(
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_ASSESSMENT,
            status="active",
            source="f3-test",
            valid_until_utc=now + timedelta(days=7),
            created_at_utc=now,
            updated_at_utc=now,
        )
        db.add(entitlement)
        db.flush()
        schedule_entitlement_lifecycle(
            db,
            tenant_id=tenant["tenant_id"],
            entitlement=entitlement,
            activation_event=EVENT_ASSESSMENT_ACTIVATED,
        )
        db.commit()

        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type.in_([
                EVENT_ASSESSMENT_ACTIVATED,
                EVENT_ASSESSMENT_EXPIRING,
                EVENT_ASSESSMENT_EXPIRED,
            ]),
        ).all()
        assert {row.event_type for row in rows} == {
            EVENT_ASSESSMENT_ACTIVATED,
            EVENT_ASSESSMENT_EXPIRING,
            EVENT_ASSESSMENT_EXPIRED,
        }
        warning = next(row for row in rows if row.event_type == EVENT_ASSESSMENT_EXPIRING)
        expiry = next(row for row in rows if row.event_type == EVENT_ASSESSMENT_EXPIRED)
        assert warning.scheduled_at_utc < expiry.scheduled_at_utc


def test_consumed_validation_credit_schedules_48h_warning(
    client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={"primary_notification_email": "validation@example.com", "preferred_language": "de"},
    )
    consumed_at = datetime.now(timezone.utc) - timedelta(days=1)
    with SessionLocal() as db:
        db.add(
            TenantScanCredit(
                tenant_id=tenant["tenant_id"],
                product_code=PRODUCT_VALIDATION_CHECK,
                status="consumed",
                source="f3-test",
                source_purchase_id=None,
                consumed_scan_id="f3-validation-scan",
                created_at_utc=consumed_at,
                consumed_at_utc=consumed_at,
            )
        )
        db.commit()
    with SessionLocal() as db:
        discover_scan_lifecycle_events(db)
        discover_scan_lifecycle_events(db)
        db.commit()
        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_VALIDATION_EXPIRING,
        ).all()
        assert len(rows) == 1
        assert "f3-validation-scan" in rows[0].payload_json
