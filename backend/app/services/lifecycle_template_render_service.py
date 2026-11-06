from __future__ import annotations

import html
from typing import Any

from app.services.email_template_service import render_email_template
from app.services.lifecycle_email_service import (
    EVENT_ASSESSMENT_ACTIVATED,
    EVENT_ASSESSMENT_EXPIRED,
    EVENT_ASSESSMENT_EXPIRING,
    EVENT_ASSESSMENT_EXTENDED,
    EVENT_QUICK_ASSESSMENT_ACTIVATED,
    EVENT_QUICK_ASSESSMENT_EXPIRED,
    EVENT_QUICK_ASSESSMENT_EXPIRING,
    EVENT_REGISTRATION_COMPLETED,
    EVENT_SCAN_COMPLETED,
    EVENT_SCAN_FAILED,
    EVENT_SCAN_STARTED,
    EVENT_VALIDATION_AVAILABLE,
    EVENT_VALIDATION_COMPLETED,
    EVENT_VALIDATION_EXPIRING,
    _event_copy,
)


def _safe_context(payload: dict[str, Any]) -> dict[str, str]:
    return {
        "environment_name": html.escape(str(payload.get("environment_name") or "")),
        "scan_id": html.escape(str(payload.get("scan_id") or "")),
        "report_url": html.escape(str(payload.get("report_url") or ""), quote=True),
        "valid_until": html.escape(str(payload.get("valid_until_utc") or "")),
        "data_score": html.escape(str(payload.get("data_score") or "")),
        "error_message": html.escape(str(payload.get("error_message") or "")),
        "baseline_scan_id": html.escape(str(payload.get("baseline_scan_id") or "")),
    }


def _strip_empty_report_link(body: str) -> str:
    for label in ("Open BCSentinel report", "BCSentinel Report öffnen"):
        body = body.replace(f'<p><a href="">{label}</a></p>', "")
    return body


def render_lifecycle_event(
    db,
    *,
    event_type: str,
    language: str,
    payload: dict[str, Any],
) -> tuple[str, str]:
    """Render canonical lifecycle copy through the editable admin template catalog.

    Unknown/historical variants intentionally fall back to the legacy renderer so
    existing queued rows remain deliverable during rollout.
    """
    key: str | None = None

    if event_type == EVENT_REGISTRATION_COMPLETED:
        key = "lifecycle_registration_completed"
    elif event_type == EVENT_SCAN_STARTED:
        key = "lifecycle_scan_started"
    elif event_type == EVENT_SCAN_COMPLETED:
        key = "lifecycle_scan_completed"
    elif event_type == EVENT_SCAN_FAILED:
        key = "lifecycle_scan_failed"
    elif event_type == EVENT_VALIDATION_COMPLETED:
        key = "lifecycle_validation_completed"
    elif event_type == EVENT_QUICK_ASSESSMENT_ACTIVATED:
        if bool(payload.get("permanent")):
            key = "lifecycle_quick_activated_existing" if payload.get("scan_id") else "lifecycle_quick_activated_prescan"
        else:
            key = "lifecycle_quick_activated_legacy"
    elif event_type == EVENT_QUICK_ASSESSMENT_EXPIRING:
        key = "lifecycle_quick_expiring"
    elif event_type == EVENT_QUICK_ASSESSMENT_EXPIRED:
        key = "lifecycle_quick_expired"
    elif event_type == EVENT_ASSESSMENT_ACTIVATED:
        key = "lifecycle_assessment_activated"
    elif event_type == EVENT_ASSESSMENT_EXTENDED:
        key = "lifecycle_assessment_extended"
    elif event_type == EVENT_ASSESSMENT_EXPIRING:
        key = "lifecycle_assessment_expiring"
    elif event_type == EVENT_ASSESSMENT_EXPIRED:
        key = "lifecycle_assessment_expired"
    elif event_type == EVENT_VALIDATION_AVAILABLE:
        # Canonical new Validation grants are pre-scan and have no result expiry
        # until the validation credit is consumed. Preserve historical payloads.
        if payload.get("baseline_scan_id") or not payload.get("valid_until_utc"):
            key = "lifecycle_validation_available"
    elif event_type == EVENT_VALIDATION_EXPIRING:
        key = "lifecycle_validation_expiring"

    if key is None:
        return _event_copy(event_type, language, payload)

    subject, body = render_email_template(
        db,
        key,
        _safe_context(payload),
        language=language,
    )
    return subject, _strip_empty_report_link(body)
