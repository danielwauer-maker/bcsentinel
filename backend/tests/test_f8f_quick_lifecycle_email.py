from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from jose import jwt

from app.core.settings import settings
from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox
from app.services.lifecycle_email_service import EVENT_QUICK_ASSESSMENT_ACTIVATED
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


def test_quick_grant_schedules_activation_only_and_uses_secure_link_when_scan_exists(
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
        assert result["valid_until_utc"] is None
        assert result["permanent"] is True
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
            LifecycleEmailOutbox.event_type.like("quick_assessment.%"),
        ).all()
        assert len(rows) == 1
        activation = rows[0]
        assert activation.event_type == EVENT_QUICK_ASSESSMENT_ACTIVATED
        activation_payload = json.loads(activation.payload_json)
        assert activation_payload["report_url"] == result["report_url"]
        assert activation_payload["scan_id"] == "f8f-quick-lifecycle-scan"
        assert activation_payload["permanent"] is True
        assert "valid_until_utc" not in activation_payload


def test_prescan_quick_grant_schedules_activation_without_report_link(
    client, tenant_factory, auth_header_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, language="en")

    with SessionLocal() as db:
        result = grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="FIV-QUICK-LIFECYCLE-PRESCAN",
            actor="tester",
        )
        db.commit()
        assert result["scan_id"] is None
        assert result["report_url"] is None

        rows = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type.like("quick_assessment.%"),
        ).all()
        assert len(rows) == 1
        payload = json.loads(rows[0].payload_json)
        assert payload["permanent"] is True
        assert payload["scan_id"] == ""
        assert payload["report_url"] == ""


def test_quick_activation_dedupe_key_is_entitlement_scoped(
    client, tenant_factory, auth_header_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, language="en")
    deep_scan_factory(tenant_id=tenant["tenant_id"], scan_id="f8f-dedupe-scan", total_records=250_000)

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
            LifecycleEmailOutbox.event_type == EVENT_QUICK_ASSESSMENT_ACTIVATED,
        ).all()
        assert len(rows) == 1
        assert rows[0].dedupe_key.startswith("quick_assessment.activated:entitlement:")
