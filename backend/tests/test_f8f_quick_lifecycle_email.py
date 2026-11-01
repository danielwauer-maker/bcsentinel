from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from jose import jwt

from app.core.settings import settings
from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox
from app.services.lifecycle_email_service import (
    EVENT_QUICK_ASSESSMENT_ACTIVATED,
    EVENT_QUICK_ASSESSMENT_EXPIRED,
    EVENT_QUICK_ASSESSMENT_EXPIRING,
    _event_copy,
)
from app.services.operator_quick_assessment_service import grant_quick_assessment


def _enable_lifecycle(client, tenant, auth_header_factory, *, language: str = "de"):
    response = client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={
            "primary_notification_email": "quick-lifecycle@example.com",
            "preferred_language": language,
        },
    )
    assert response.status_code == 200, response.text


def _as_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def test_quick_grant_schedules_activation_warning_and_expiry_with_secure_quick_link(
    client, tenant_factory, auth_header_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, language="de")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="f8f-quick-lifecycle-scan",
        total_records=100_000,
    )

    with SessionLocal() as db:
        result = grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-LIFECYCLE-001",
            actor="tester",
        )
        db.commit()
        assert result["report_url"]
        assert "/reports/quick-assessment/f8f-quick-lifecycle-scan/html/shared?token=" in result["report_url"]

        parsed = urlparse(result["report_url"])
        token = parse_qs(parsed.query)["token"][0]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["type"] == "quick_assessment_report_share"
        assert payload["tenant_id"] == tenant["tenant_id"]
        assert payload["scan_id"] == "f8f-quick-lifecycle-scan"
        assert payload["report_type"] == "html"

        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type.in_([
                EVENT_QUICK_ASSESSMENT_ACTIVATED,
                EVENT_QUICK_ASSESSMENT_EXPIRING,
                EVENT_QUICK_ASSESSMENT_EXPIRED,
            ]),
        ).order_by(LifecycleEmailOutbox.scheduled_at_utc.asc()).all()
        assert len(rows) == 3
        by_event = {row.event_type: row for row in rows}
        assert set(by_event) == {
            EVENT_QUICK_ASSESSMENT_ACTIVATED,
            EVENT_QUICK_ASSESSMENT_EXPIRING,
            EVENT_QUICK_ASSESSMENT_EXPIRED,
        }

        activation = by_event[EVENT_QUICK_ASSESSMENT_ACTIVATED]
        warning = by_event[EVENT_QUICK_ASSESSMENT_EXPIRING]
        expired = by_event[EVENT_QUICK_ASSESSMENT_EXPIRED]
        assert activation.language == "de"
        assert warning.language == "de"
        assert expired.language == "de"
        assert timedelta(hours=47, minutes=59) <= (
            _as_utc(expired.scheduled_at_utc) - _as_utc(warning.scheduled_at_utc)
        ) <= timedelta(hours=48, minutes=1)

        activation_payload = json.loads(activation.payload_json)
        warning_payload = json.loads(warning.payload_json)
        expired_payload = json.loads(expired.payload_json)
        assert activation_payload["report_url"] == result["report_url"]
        assert warning_payload["report_url"] == result["report_url"]
        assert expired_payload["report_url"] == result["report_url"]
        assert activation_payload["scan_id"] == "f8f-quick-lifecycle-scan"
        assert warning_payload["valid_until_utc"] == expired_payload["valid_until_utc"]


def test_quick_lifecycle_copy_is_specific_and_bilingual():
    payload = {
        "scan_id": "scan-123",
        "valid_until_utc": "2026-11-08T12:00:00Z",
        "report_url": "https://example.test/reports/quick-assessment/scan-123/html/shared?token=abc",
    }

    de_subject, de_body = _event_copy(EVENT_QUICK_ASSESSMENT_ACTIVATED, "de", payload)
    en_subject, en_body = _event_copy(EVENT_QUICK_ASSESSMENT_ACTIVATED, "en", payload)
    assert de_subject == "BCSentinel Quick Assessment aktiviert"
    assert "priorisierten Quick-Assessment-Ergebnisse" in de_body
    assert "BCSentinel Report öffnen" in de_body
    assert en_subject == "BCSentinel Quick Assessment activated"
    assert "prioritized Quick Assessment results" in en_body
    assert "Open BCSentinel report" in en_body

    de_subject, de_body = _event_copy(EVENT_QUICK_ASSESSMENT_EXPIRING, "de", payload)
    en_subject, en_body = _event_copy(EVENT_QUICK_ASSESSMENT_EXPIRING, "en", payload)
    assert "läuft bald ab" in de_subject
    assert "Live-Zugriff" in de_body
    assert "expires soon" in en_subject
    assert "live access ends" in en_body

    de_subject, de_body = _event_copy(EVENT_QUICK_ASSESSMENT_EXPIRED, "de", payload)
    en_subject, en_body = _event_copy(EVENT_QUICK_ASSESSMENT_EXPIRED, "en", payload)
    assert "abgelaufen" in de_subject
    assert "Full Assessment" in de_body
    assert "expired" in en_subject
    assert "Full Assessment" in en_body


def test_quick_lifecycle_dedupe_keys_are_entitlement_scoped(
    client, tenant_factory, auth_header_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, language="en")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="f8f-dedupe-scan",
        total_records=250_000,
    )

    with SessionLocal() as db:
        grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-LIFECYCLE-DEDUP",
            actor="tester",
        )
        db.commit()

        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type.in_([
                EVENT_QUICK_ASSESSMENT_ACTIVATED,
                EVENT_QUICK_ASSESSMENT_EXPIRING,
                EVENT_QUICK_ASSESSMENT_EXPIRED,
            ]),
        ).all()
        assert len(rows) == 3
        keys = {row.dedupe_key for row in rows}
        assert len(keys) == 3
        assert all(":entitlement:" in key for key in keys)
        assert any(key.startswith("quick_assessment.activated:entitlement:") for key in keys)
        assert any(key.startswith("quick_assessment.expiring:entitlement:") for key in keys)
        assert any(key.startswith("quick_assessment.expired:entitlement:") for key in keys)
