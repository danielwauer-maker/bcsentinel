from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import RemediationActionRead, RemediationAuditRead
from app.security.tenant import enforce_tenant_match, load_authenticated_tenant, require_tenant_headers

router = APIRouter(prefix="/remediation", tags=["remediation"])

CANONICAL_STATUSES = {"open", "in_progress", "blocked", "completed", "cancelled"}
CANONICAL_PRIORITIES = {"critical", "high", "medium", "low"}


class RemediationAuditPayload(BaseModel):
    changed_at_utc: datetime
    changed_by_principal_id: Optional[str] = None
    changed_field_or_status: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None


class RemediationActionSyncPayload(BaseModel):
    tenant_id: str
    company_id: str
    action_id: str
    finding_key: str
    title: str
    description: str = ""
    recommendation_ref: Optional[str] = None
    status: str
    priority: str
    owner_principal_id: Optional[str] = None
    owner_display_name: Optional[str] = None
    due_at_utc: Optional[datetime] = None
    started_at_utc: Optional[datetime] = None
    completed_at_utc: Optional[datetime] = None
    cancelled_at_utc: Optional[datetime] = None
    blocked_reason: Optional[str] = None
    completion_note: Optional[str] = None
    validation_result_ref: Optional[str] = None
    source: str = "manual"
    created_at_utc: datetime
    updated_at_utc: datetime
    audit: list[RemediationAuditPayload] = Field(default_factory=list)


def _norm(value: str) -> str:
    return (value or "").strip().lower().replace(" ", "_")


def _serialize_action(row: RemediationActionRead) -> dict[str, object]:
    return {
        "action_id": row.action_id,
        "tenant_id": row.tenant_id,
        "company_id": row.company_id,
        "finding_key": row.finding_key,
        "title": row.title,
        "description": row.description,
        "recommendation_ref": row.recommendation_ref,
        "status": row.status,
        "priority": row.priority,
        "owner_principal_id": row.owner_principal_id,
        "owner_display_name": row.owner_display_name,
        "due_at_utc": row.due_at_utc,
        "started_at_utc": row.started_at_utc,
        "completed_at_utc": row.completed_at_utc,
        "cancelled_at_utc": row.cancelled_at_utc,
        "blocked_reason": row.blocked_reason,
        "completion_note": row.completion_note,
        "validation_result_ref": row.validation_result_ref,
        "source": row.source,
        "created_at_utc": row.created_at_utc,
        "updated_at_utc": row.updated_at_utc,
    }


@router.post("/sync")
def sync_remediation_action(
    payload: RemediationActionSyncPayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")
    status = _norm(payload.status)
    priority = _norm(payload.priority)
    if status not in CANONICAL_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid remediation status.")
    if priority not in CANONICAL_PRIORITIES:
        raise HTTPException(status_code=400, detail="Invalid remediation priority.")

    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        row = db.scalar(
            select(RemediationActionRead).where(
                RemediationActionRead.action_id == payload.action_id,
                RemediationActionRead.tenant_id == header_tenant_id,
            )
        )
        if row is None:
            row = RemediationActionRead(action_id=payload.action_id, tenant_id=payload.tenant_id)
            db.add(row)

        row.company_id = payload.company_id
        row.finding_key = payload.finding_key
        row.title = payload.title
        row.description = payload.description
        row.recommendation_ref = payload.recommendation_ref
        row.status = status
        row.priority = priority
        row.owner_principal_id = payload.owner_principal_id
        row.owner_display_name = payload.owner_display_name
        row.due_at_utc = payload.due_at_utc
        row.started_at_utc = payload.started_at_utc
        row.completed_at_utc = payload.completed_at_utc
        row.cancelled_at_utc = payload.cancelled_at_utc
        row.blocked_reason = payload.blocked_reason
        row.completion_note = payload.completion_note
        row.validation_result_ref = payload.validation_result_ref
        row.source = _norm(payload.source) or "manual"
        row.created_at_utc = payload.created_at_utc
        row.updated_at_utc = payload.updated_at_utc
        row.synced_at_utc = datetime.now(timezone.utc)

        existing_history = {
            (x.changed_at_utc, x.changed_field_or_status, x.previous_value or "", x.new_value or "")
            for x in db.scalars(
                select(RemediationAuditRead).where(
                    RemediationAuditRead.action_id == payload.action_id,
                    RemediationAuditRead.tenant_id == header_tenant_id,
                )
            )
        }
        for item in payload.audit:
            key = (item.changed_at_utc, item.changed_field_or_status, item.previous_value or "", item.new_value or "")
            if key in existing_history:
                continue
            db.add(
                RemediationAuditRead(
                    action_id=payload.action_id,
                    tenant_id=payload.tenant_id,
                    company_id=payload.company_id,
                    changed_at_utc=item.changed_at_utc,
                    changed_by_principal_id=item.changed_by_principal_id,
                    changed_field_or_status=item.changed_field_or_status,
                    previous_value=item.previous_value,
                    new_value=item.new_value,
                )
            )
        db.commit()

    return {"status": "synced", "action_id": payload.action_id}


@router.get("/actions")
def list_actions(
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    company_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        stmt = select(RemediationActionRead).where(RemediationActionRead.tenant_id == header_tenant_id)
        if status:
            normalized = _norm(status)
            if normalized not in CANONICAL_STATUSES:
                raise HTTPException(status_code=400, detail="Invalid remediation status filter.")
            stmt = stmt.where(RemediationActionRead.status == normalized)
        if priority:
            normalized = _norm(priority)
            if normalized not in CANONICAL_PRIORITIES:
                raise HTTPException(status_code=400, detail="Invalid remediation priority filter.")
            stmt = stmt.where(RemediationActionRead.priority == normalized)
        if company_id:
            stmt = stmt.where(RemediationActionRead.company_id == company_id)
        stmt = stmt.order_by(RemediationActionRead.updated_at_utc.desc()).offset(offset).limit(limit)
        rows = list(db.scalars(stmt))
        return {"items": [_serialize_action(row) for row in rows], "limit": limit, "offset": offset}


@router.get("/actions/{action_id}")
def get_action(
    action_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        row = db.scalar(
            select(RemediationActionRead).where(
                RemediationActionRead.action_id == action_id,
                RemediationActionRead.tenant_id == header_tenant_id,
            )
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Remediation action not found.")
        return _serialize_action(row)


@router.get("/actions/{action_id}/history")
def get_action_history(
    action_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        exists = db.scalar(
            select(RemediationActionRead.id).where(
                RemediationActionRead.action_id == action_id,
                RemediationActionRead.tenant_id == header_tenant_id,
            )
        )
        if exists is None:
            raise HTTPException(status_code=404, detail="Remediation action not found.")
        rows = list(
            db.scalars(
                select(RemediationAuditRead)
                .where(
                    RemediationAuditRead.action_id == action_id,
                    RemediationAuditRead.tenant_id == header_tenant_id,
                )
                .order_by(RemediationAuditRead.changed_at_utc.desc())
            )
        )
        return {
            "items": [
                {
                    "changed_at_utc": row.changed_at_utc,
                    "changed_by_principal_id": row.changed_by_principal_id,
                    "changed_field_or_status": row.changed_field_or_status,
                    "previous_value": row.previous_value,
                    "new_value": row.new_value,
                }
                for row in rows
            ]
        }


@router.get("/metrics")
def remediation_metrics(
    company_id: Optional[str] = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        filters = [RemediationActionRead.tenant_id == header_tenant_id]
        if company_id:
            filters.append(RemediationActionRead.company_id == company_id)
        counts = dict(
            db.execute(
                select(RemediationActionRead.status, func.count(RemediationActionRead.id))
                .where(*filters)
                .group_by(RemediationActionRead.status)
            ).all()
        )
        total = sum(int(value) for value in counts.values())
        overdue = db.scalar(
            select(func.count(RemediationActionRead.id)).where(
                *filters,
                RemediationActionRead.due_at_utc.is_not(None),
                RemediationActionRead.due_at_utc < datetime.now(timezone.utc),
                RemediationActionRead.status.not_in(["completed", "cancelled"]),
            )
        ) or 0
        return {
            "total": total,
            "open": int(counts.get("open", 0)),
            "in_progress": int(counts.get("in_progress", 0)),
            "blocked": int(counts.get("blocked", 0)),
            "completed": int(counts.get("completed", 0)),
            "cancelled": int(counts.get("cancelled", 0)),
            "overdue": int(overdue),
            "validated_resolved": None,
            "note": "completed does not imply validated resolved",
        }
