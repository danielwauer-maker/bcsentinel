from __future__ import annotations

import pytest

from app.db import SessionLocal
from app.services.email_template_service import (
    ensure_default_email_templates,
    list_email_templates_for_admin,
    storage_key,
    update_email_template,
)
from app.services.lifecycle_email_service import (
    EVENT_ASSESSMENT_ACTIVATED,
    EVENT_QUICK_ASSESSMENT_ACTIVATED,
    EVENT_SCAN_COMPLETED,
    EVENT_SCAN_STARTED,
    EVENT_VALIDATION_AVAILABLE,
)
from app.services.lifecycle_template_render_service import render_lifecycle_event


def test_admin_catalog_contains_customer_lifecycle_templates_in_de_and_en():
    expected = {
        "lifecycle_registration_completed",
        "lifecycle_scan_started",
        "lifecycle_scan_completed",
        "lifecycle_scan_failed",
        "lifecycle_quick_activated_existing",
        "lifecycle_quick_activated_prescan",
        "lifecycle_assessment_activated",
        "lifecycle_assessment_expiring",
        "lifecycle_assessment_expired",
        "lifecycle_validation_available",
        "lifecycle_validation_completed",
        "lifecycle_validation_expiring",
    }
    with SessionLocal() as db:
        ensure_default_email_templates(db)
        templates = list_email_templates_for_admin(db)
    pairs = {(str(item["base_key"]), str(item["language"])) for item in templates}
    for key in expected:
        assert (key, "en") in pairs
        assert (key, "de") in pairs


def test_admin_edit_is_used_by_canonical_lifecycle_renderer():
    with SessionLocal() as db:
        ensure_default_email_templates(db)
        key = storage_key("lifecycle_scan_started", "de")
        update_email_template(
            db,
            key=key,
            subject_template="Scan gestartet · bearbeitet",
            html_template="<p>Bearbeitet: <strong>{{ scan_id }}</strong></p>",
        )
        subject, body = render_lifecycle_event(
            db,
            event_type=EVENT_SCAN_STARTED,
            language="de",
            payload={"scan_id": "SCAN-001"},
        )
    assert subject == "Scan gestartet · bearbeitet"
    assert "SCAN-001" in body
    assert "Bearbeitet" in body


def test_quick_permanent_selects_prescan_or_existing_scan_template():
    with SessionLocal() as db:
        prescan_subject, prescan_body = render_lifecycle_event(
            db,
            event_type=EVENT_QUICK_ASSESSMENT_ACTIVATED,
            language="en",
            payload={"permanent": True},
        )
        existing_subject, existing_body = render_lifecycle_event(
            db,
            event_type=EVENT_QUICK_ASSESSMENT_ACTIVATED,
            language="en",
            payload={
                "permanent": True,
                "scan_id": "SCAN-001",
                "report_url": "https://example.invalid/report",
            },
        )
    assert prescan_subject == "BCSentinel Quick Assessment activated"
    assert "Start the included first Data Health Scan" in prescan_body
    assert existing_subject == "BCSentinel Quick Assessment activated"
    assert "existing Data Health Scan" in existing_body
    assert "https://example.invalid/report" in existing_body


def test_full_and_validation_templates_preserve_time_and_baseline_semantics():
    with SessionLocal() as db:
        assessment_subject, assessment_body = render_lifecycle_event(
            db,
            event_type=EVENT_ASSESSMENT_ACTIVATED,
            language="en",
            payload={
                "valid_until_utc": "2026-11-10T12:00:00Z",
                "report_url": "https://example.invalid/full",
            },
        )
        validation_subject, validation_body = render_lifecycle_event(
            db,
            event_type=EVENT_VALIDATION_AVAILABLE,
            language="en",
            payload={"baseline_scan_id": "BASE-001"},
        )
    assert assessment_subject == "BCSentinel Assessment activated"
    assert "2026-11-10T12:00:00Z" in assessment_body
    assert "https://example.invalid/full" in assessment_body
    assert validation_subject == "BCSentinel Validation available"
    assert "7-day full Validation result window begins with that new scan" in validation_body
    assert "BASE-001" in validation_body


def test_scan_completed_template_escapes_payload_and_keeps_report_link():
    with SessionLocal() as db:
        subject, body = render_lifecycle_event(
            db,
            event_type=EVENT_SCAN_COMPLETED,
            language="de",
            payload={
                "scan_id": "<SCAN-001>",
                "data_score": 87,
                "report_url": "https://example.invalid/report?a=1&b=2",
            },
        )
    assert subject == "BCSentinel Scan abgeschlossen"
    assert "&lt;SCAN-001&gt;" in body
    assert "87/100" in body
    assert "https://example.invalid/report?a=1&amp;b=2" in body


def test_lifecycle_template_rejects_unknown_placeholders_and_active_content():
    with SessionLocal() as db:
        ensure_default_email_templates(db)
        key = storage_key("lifecycle_scan_started", "en")
        with pytest.raises(ValueError):
            update_email_template(
                db,
                key=key,
                subject_template="Unsafe {{ unknown_value }}",
                html_template="<script>alert(1)</script>",
            )
