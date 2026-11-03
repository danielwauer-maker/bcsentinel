from __future__ import annotations

import json

from app.db import SessionLocal
from app.lifecycle_models import LifecycleEmailOutbox
from app.services.fiverr_next_purchase_service import (
    build_fiverr_next_purchase_recommendation,
    render_fiverr_next_purchase_html,
)
from app.services.lifecycle_email_service import EVENT_SCAN_COMPLETED, queue_scan_completed
from app.services.lifecycle_worker_service import process_due_outbox_safely
from app.services.operator_commercial_service import grant_assessment
from app.services.operator_quick_assessment_service import grant_quick_assessment


def _enable_lifecycle(client, tenant, auth_header_factory, *, language: str = "de"):
    response = client.put(
        "/tenant/lifecycle-profile",
        headers=auth_header_factory(tenant),
        json={
            "primary_notification_email": "next-purchase@example.com",
            "preferred_language": language,
        },
    )
    assert response.status_code == 200, response.text


def test_free_report_recommends_basic_quick_with_volume_addon(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="next-free-medium",
        total_records=800_000,
    )

    with SessionLocal() as db:
        recommendation = build_fiverr_next_purchase_recommendation(
            db,
            tenant_id=tenant["tenant_id"],
            scan_id="next-free-medium",
        )

    assert recommendation is not None
    assert recommendation["current_report_variant"] == "free-health"
    assert recommendation["product_code"] == "quick_assessment"
    assert recommendation["fiverr_package"] == "BASIC"
    assert recommendation["base_gig_price"] == 149.0
    assert recommendation["total_price"] == 279.0
    assert recommendation["addon_price"] == 130.0
    assert recommendation["requires_new_scan"] is False


def test_quick_report_recommends_advanced_full_without_rescan(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="next-quick-medium",
        total_records=800_000,
    )
    with SessionLocal() as db:
        grant_quick_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="NEXT-QUICK-001",
            actor="tester",
        )
        db.commit()

        recommendation = build_fiverr_next_purchase_recommendation(
            db,
            tenant_id=tenant["tenant_id"],
            scan_id="next-quick-medium",
        )

    assert recommendation is not None
    assert recommendation["current_report_variant"] == "quick-assessment"
    assert recommendation["product_code"] == "assessment"
    assert recommendation["fiverr_package"] == "ADVANCED"
    assert recommendation["base_gig_price"] == 349.0
    assert recommendation["total_price"] == 549.0
    assert recommendation["addon_price"] == 200.0
    assert recommendation["requires_new_scan"] is False


def test_full_report_recommends_validation_after_remediation(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="next-full-medium",
        total_records=800_000,
    )
    with SessionLocal() as db:
        grant_assessment(
            db,
            tenant_id=tenant["tenant_id"],
            sales_channel="fiverr",
            external_order_reference="NEXT-FULL-001",
            actor="tester",
        )
        db.commit()

        recommendation = build_fiverr_next_purchase_recommendation(
            db,
            tenant_id=tenant["tenant_id"],
            scan_id="next-full-medium",
        )

    assert recommendation is not None
    assert recommendation["current_report_variant"] == "assessment"
    assert recommendation["product_code"] == "validation_check"
    assert recommendation["fiverr_package"] == "VALIDATION"
    assert recommendation["base_gig_price"] == 179.0
    assert recommendation["total_price"] == 289.0
    assert recommendation["addon_price"] == 110.0
    assert recommendation["requires_new_scan"] is True
    assert recommendation["after_remediation"] is True


def test_above_20m_uses_custom_offer_instead_of_guessing_addon(
    tenant_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="next-custom",
        total_records=20_000_001,
    )

    with SessionLocal() as db:
        recommendation = build_fiverr_next_purchase_recommendation(
            db,
            tenant_id=tenant["tenant_id"],
            scan_id="next-custom",
        )

    assert recommendation is not None
    assert recommendation["custom_offer_required"] is True
    assert recommendation["total_price"] is None
    assert recommendation["addon_price"] is None
    assert recommendation["recommendation_type"] == "individual_review"


def test_renderer_explains_gig_addon_and_no_rescan_in_de_and_en():
    recommendation = {
        "total_records": 800_000,
        "product_name": "Full Assessment",
        "fiverr_package": "ADVANCED",
        "base_gig_price": 349.0,
        "total_price": 549.0,
        "addon_price": 200.0,
        "custom_offer_required": False,
        "after_remediation": False,
    }

    de = render_fiverr_next_purchase_html(recommendation, language="de")
    en = render_fiverr_next_purchase_html(recommendation, language="en")

    assert "800.000 Datensätze" in de
    assert "ADVANCED – Full Assessment" in de
    assert "$349" in de and "$200" in de and "$549" in de
    assert "kein neuer Scan erforderlich" in de

    assert "800,000 records" in en
    assert "ADVANCED – Full Assessment" in en
    assert "$349" in en and "$200" in en and "$549" in en
    assert "No new scan is required" in en


def test_scan_completed_worker_appends_authoritative_fiverr_guidance(
    monkeypatch, client, tenant_factory, auth_header_factory, deep_scan_factory
):
    tenant = tenant_factory(plan="free", license_status="active")
    _enable_lifecycle(client, tenant, auth_header_factory, language="de")
    deep_scan_factory(
        tenant_id=tenant["tenant_id"],
        scan_id="next-worker-medium",
        total_records=800_000,
    )

    with SessionLocal() as db:
        queue_scan_completed(
            db,
            tenant_id=tenant["tenant_id"],
            scan_id="next-worker-medium",
            data_score=68,
        )
        db.commit()
        row = db.query(LifecycleEmailOutbox).filter(
            LifecycleEmailOutbox.tenant_id == tenant["tenant_id"],
            LifecycleEmailOutbox.event_type == EVENT_SCAN_COMPLETED,
        ).one()
        payload = json.loads(row.payload_json)
        assert "next_purchase" not in payload

    sent = []

    def fake_send(**kwargs):
        sent.append(kwargs)

    monkeypatch.setattr("app.services.lifecycle_worker_service._send_html_email", fake_send)
    with SessionLocal() as db:
        result = process_due_outbox_safely(db)
        db.commit()

    assert result["failed"] == 0
    completion = next(message for message in sent if "Scan abgeschlossen" in message["subject"])
    body = completion["html_body"]
    assert "Ihr nächster Schritt auf Fiverr" in body
    assert "BASIC – Quick Assessment" in body
    assert "$149" in body
    assert "$130" in body
    assert "$279" in body
    assert "kein neuer Scan erforderlich" in body
