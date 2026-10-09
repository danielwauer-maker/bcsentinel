from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.notification_models import NotificationSettingsRead
from app.security.tenant import enforce_tenant_match, load_authenticated_tenant, require_tenant_headers

router = APIRouter(prefix="/notifications", tags=["notifications"])

CANONICAL_EVENT_TYPES = {
    "scan.completed",
    "scan.failed",
    "finding.new_critical",
    "finding.regressed",
    "monitoring.score_deteriorated",
    "validation.completed",
    "remediation.blocked",
    "remediation.overdue",
}
CANONICAL_CHANNELS = {"email"}


class NotificationSettingsSyncPayload(BaseModel):
    tenant_id: str
    company_id: str
    notifications_enabled: bool
    preferred_language: str = "en"
    configured_event_types: list[str] = Field(default_factory=list)
    enabled_event_types: list[str] = Field(default_factory=list)
    recipient_count: int = Field(default=0, ge=0)
    enabled_recipient_count: int = Field(default=0, ge=0)
    channels: list[str] = Field(default_factory=list)
    template_languages: list[str] = Field(default_factory=list)
    sent_deliveries: int = Field(default=0, ge=0)
    failed_deliveries: int = Field(default=0, ge=0)
    suppressed_deliveries: int = Field(default=0, ge=0)
    last_successful_delivery_at_utc: Optional[datetime] = None
    last_failed_delivery_at_utc: Optional[datetime] = None
    safe_last_failure_summary: Optional[str] = Field(default=None, max_length=250)
    bc_updated_at_utc: datetime


def _normalized_unique(values: list[str]) -> list[str]:
    return sorted({str(value or "").strip().lower() for value in values if str(value or "").strip()})


def _json_list(value: str) -> list[str]:
    try:
        parsed = json.loads(value or "[]")
    except (TypeError, ValueError):
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def _serialize(row: NotificationSettingsRead) -> dict[str, object]:
    sent = int(row.sent_deliveries or 0)
    failed = int(row.failed_deliveries or 0)
    attempted = sent + failed
    success_rate = round((sent / attempted) * 100.0, 2) if attempted > 0 else None
    return {
        "tenant_id": row.tenant_id,
        "company_id": row.company_id,
        "notifications_enabled": bool(row.notifications_enabled),
        "preferred_language": row.preferred_language,
        "configured_event_types": _json_list(row.configured_event_types_json),
        "enabled_event_types": _json_list(row.enabled_event_types_json),
        "recipient_summary": {
            "configured": int(row.recipient_count or 0),
            "enabled": int(row.enabled_recipient_count or 0),
        },
        "channel_summary": _json_list(row.channels_json),
        "template_language_summary": _json_list(row.template_languages_json),
        "delivery_summary": {
            "sent": sent,
            "failed": failed,
            "suppressed": int(row.suppressed_deliveries or 0),
            "success_rate_pct": success_rate,
            "last_successful_delivery_at_utc": row.last_successful_delivery_at_utc,
            "last_failed_delivery_at_utc": row.last_failed_delivery_at_utc,
            "safe_last_failure_summary": row.safe_last_failure_summary,
        },
        "bc_updated_at_utc": row.bc_updated_at_utc,
        "synced_at_utc": row.synced_at_utc,
        "manage_in_business_central_hint": True,
        "dashboard_mode": "read_only",
    }


@router.post("/read-model/sync")
def sync_notification_settings(
    payload: NotificationSettingsSyncPayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")

    configured = _normalized_unique(payload.configured_event_types)
    enabled = _normalized_unique(payload.enabled_event_types)
    channels = _normalized_unique(payload.channels)
    template_languages = _normalized_unique(payload.template_languages)

    unknown_events = sorted((set(configured) | set(enabled)) - CANONICAL_EVENT_TYPES)
    if unknown_events:
        raise HTTPException(status_code=400, detail="Unknown notification event type.")
    if not set(enabled).issubset(set(configured)):
        raise HTTPException(status_code=400, detail="Enabled event types must be configured event types.")
    if set(channels) - CANONICAL_CHANNELS:
        raise HTTPException(status_code=400, detail="Unsupported notification channel.")
    if payload.enabled_recipient_count > payload.recipient_count:
        raise HTTPException(status_code=400, detail="Enabled recipient count cannot exceed recipient count.")

    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        row = db.scalar(
            select(NotificationSettingsRead).where(
                NotificationSettingsRead.tenant_id == header_tenant_id,
                NotificationSettingsRead.company_id == payload.company_id,
            )
        )
        if row is None:
            row = NotificationSettingsRead(tenant_id=payload.tenant_id, company_id=payload.company_id)
            db.add(row)

        row.notifications_enabled = payload.notifications_enabled
        row.preferred_language = (payload.preferred_language or "en").strip().lower()[:10]
        row.configured_event_types_json = json.dumps(configured, separators=(",", ":"))
        row.enabled_event_types_json = json.dumps(enabled, separators=(",", ":"))
        row.recipient_count = payload.recipient_count
        row.enabled_recipient_count = payload.enabled_recipient_count
        row.channels_json = json.dumps(channels, separators=(",", ":"))
        row.template_languages_json = json.dumps(template_languages, separators=(",", ":"))
        row.sent_deliveries = payload.sent_deliveries
        row.failed_deliveries = payload.failed_deliveries
        row.suppressed_deliveries = payload.suppressed_deliveries
        row.last_successful_delivery_at_utc = payload.last_successful_delivery_at_utc
        row.last_failed_delivery_at_utc = payload.last_failed_delivery_at_utc
        row.safe_last_failure_summary = payload.safe_last_failure_summary
        row.bc_updated_at_utc = payload.bc_updated_at_utc
        row.synced_at_utc = datetime.now(timezone.utc)
        db.commit()

    return {"status": "synced", "company_id": payload.company_id}


@router.get("/settings")
def get_notification_settings(
    company_id: Optional[str] = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        stmt = select(NotificationSettingsRead).where(NotificationSettingsRead.tenant_id == header_tenant_id)
        if company_id:
            stmt = stmt.where(NotificationSettingsRead.company_id == company_id)
        rows = list(db.scalars(stmt.order_by(NotificationSettingsRead.company_id.asc())))
        return {
            "items": [_serialize(row) for row in rows],
            "dashboard_mode": "read_only",
            "manage_in_business_central_hint": True,
        }
