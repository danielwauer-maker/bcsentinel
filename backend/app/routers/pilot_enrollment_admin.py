"""Operator-only pilot enrollment administration; plaintext token returned ONCE on approval."""
from __future__ import annotations

import secrets

from fastapi import Header, Request
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.pilot_enrollment_models import PilotEnrollment, PilotEnrollmentAudit
from app.routers.operator_admin import require_operator
from app.services.pilot_enrollment_service import (
    EnrollmentRejected, change_status, create_enrollment, issue_token,
)
from app.services.tenant_registration_service import build_registration_identity

def require_pilot_admin_security(
    request: Request,
    x_pilot_operator_key: str | None = Header(default=None, alias="X-Pilot-Operator-Key"),
    actor: str = Depends(require_operator),
) -> None:
    """Require separate operator-secret authorization; deny browser-origin requests.

    Reverse proxy must additionally restrict this internal route to the trusted
    admin network. Never use client-controlled forwarded headers as proof.
    """
    expected = (settings.PILOT_ENROLLMENT_ADMIN_KEY or "").strip()
    if not expected or len(expected) < 32 or not x_pilot_operator_key or not secrets.compare_digest(
        x_pilot_operator_key, expected
    ):
        raise HTTPException(status_code=403, detail="Pilot operator access denied.")
    if request.headers.get("origin") or request.headers.get("sec-fetch-site"):
        raise HTTPException(status_code=403, detail="Browser-origin pilot administration denied.")


router = APIRouter(
    prefix="/internal/pilot/enrollments",
    tags=["pilot-enrollment"],
    dependencies=[Depends(require_pilot_admin_security)],
)


class EnrollmentCreate(BaseModel):
    entra_tenant_id: str
    environment_name: str
    environment_type: str
    company_id: str
    company_name: str
    contact_email: str
    authorized_email: str
    commercial_profile: str = Field(min_length=1, max_length=60)


class TokenIssue(BaseModel):
    lifetime_hours: int = Field(default=72, ge=1, le=168)


def _enabled() -> None:
    if not settings.PILOT_ENROLLMENT_ENABLED:
        raise HTTPException(status_code=404, detail="Pilot enrollment is disabled.")


def _row(db, enrollment_id: int) -> PilotEnrollment:
    row = db.get(PilotEnrollment, enrollment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Enrollment not found.")
    return row


def _public(row: PilotEnrollment) -> dict:
    return {
        "id": row.id, "status": row.status,
        "contact_email": row.contact_email, "authorized_email": row.authorized_email,
        "identity_key": row.identity_key, "commercial_profile": row.commercial_profile,
        "registered_tenant_id": row.registered_tenant_id,
        "token_expires_at_utc": row.token_expires_at_utc,
        "created_at_utc": row.created_at_utc, "updated_at_utc": row.updated_at_utc,
    }


@router.post("")
def create_pilot_enrollment(
    payload: EnrollmentCreate, response: Response,
    actor: str = Depends(require_operator),
):
    _enabled()
    response.headers["Cache-Control"] = "no-store"
    try:
        identity = build_registration_identity(
            entra_tenant_id=payload.entra_tenant_id,
            environment_name=payload.environment_name,
            environment_type=payload.environment_type,
            company_id=payload.company_id,
            company_name=payload.company_name,
        )
        with SessionLocal() as db:
            row = create_enrollment(
                db, identity_key=identity.key, contact_email=payload.contact_email,
                authorized_email=payload.authorized_email,
                commercial_profile=payload.commercial_profile, actor=actor,
            )
            db.commit()
            db.refresh(row)
            return _public(row)
    except (ValueError, EnrollmentRejected) as exc:
        raise HTTPException(status_code=422, detail="Invalid enrollment details.") from exc


@router.get("")
def list_pilot_enrollments(
    response: Response, actor: str = Depends(require_operator),
):
    _enabled()
    response.headers["Cache-Control"] = "no-store"
    with SessionLocal() as db:
        rows = db.scalars(select(PilotEnrollment).order_by(PilotEnrollment.id.desc()).limit(100)).all()
        return {"enrollments": [_public(row) for row in rows]}


@router.get("/{enrollment_id}")
def show_pilot_enrollment(
    enrollment_id: int, response: Response, actor: str = Depends(require_operator),
):
    _enabled()
    response.headers["Cache-Control"] = "no-store"
    with SessionLocal() as db:
        row = _row(db, enrollment_id)
        history = db.scalars(select(PilotEnrollmentAudit).where(
            PilotEnrollmentAudit.enrollment_id == row.id,
        ).order_by(PilotEnrollmentAudit.id)).all()
        return {"enrollment": _public(row), "audit": [
            {"action": e.action, "actor": e.actor, "created_at_utc": e.created_at_utc}
            for e in history
        ]}


@router.post("/{enrollment_id}/approve")
def approve_pilot_enrollment(
    enrollment_id: int, payload: TokenIssue, response: Response,
    actor: str = Depends(require_operator),
):
    _enabled()
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    with SessionLocal() as db:
        row = db.scalar(select(PilotEnrollment).where(PilotEnrollment.id == enrollment_id).with_for_update())
        if row is None:
            raise HTTPException(status_code=404, detail="Enrollment not found.")
        try:
            token = issue_token(db, row, actor=actor, lifetime_hours=payload.lifetime_hours)
            db.commit()
            db.refresh(row)
            # Token is deliberately returned exactly once to the authenticated operator.
            # Subsequent status/list/audit routes never return it or its hash.
            return {"enrollment": _public(row), "enrollment_token_once": token}
        except EnrollmentRejected as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{enrollment_id}/{action}")
def transition_pilot_enrollment(
    enrollment_id: int, action: str, response: Response,
    actor: str = Depends(require_operator),
):
    _enabled()
    response.headers["Cache-Control"] = "no-store"
    if action not in {"revoke", "suspend", "activate", "expire"}:
        raise HTTPException(status_code=404, detail="Unknown enrollment transition.")
    with SessionLocal() as db:
        row = db.scalar(select(PilotEnrollment).where(PilotEnrollment.id == enrollment_id).with_for_update())
        if row is None:
            raise HTTPException(status_code=404, detail="Enrollment not found.")
        try:
            change_status(db, row, action=action, actor=actor)
            db.commit()
            db.refresh(row)
            return _public(row)
        except EnrollmentRejected as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
