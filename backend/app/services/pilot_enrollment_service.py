"""Issue #43: fail-closed, atomic BC-identity-bound pilot enrollment."""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.pilot_enrollment_models import PilotEnrollment, PilotEnrollmentAudit


class EnrollmentRejected(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _audit(db: Session, row: PilotEnrollment, action: str, actor: str) -> None:
    # No user supplied token/secret/email in audit payload.
    db.add(PilotEnrollmentAudit(
        enrollment_id=row.id, action=action, actor=actor,
        details=json.dumps({"status": row.status}, sort_keys=True),
        created_at_utc=utc_now(),
    ))


def create_enrollment(db: Session, *, identity_key: str, contact_email: str,
                      authorized_email: str, commercial_profile: str, actor: str) -> PilotEnrollment:
    if len(identity_key) != 64 or any(c not in "0123456789abcdef" for c in identity_key):
        raise EnrollmentRejected("Invalid canonical BC identity key.")
    if not commercial_profile.strip():
        raise EnrollmentRejected("Explicit commercial profile is required.")
    contact_email = contact_email.strip().lower()
    authorized_email = authorized_email.strip().lower()
    if not contact_email or not authorized_email or "@" not in authorized_email or "@" not in contact_email:
        raise EnrollmentRejected("Separate contact and authorized email must be supplied.")
    now = utc_now()
    row = PilotEnrollment(
        status="PENDING", identity_key=identity_key,
        contact_email=contact_email, authorized_email=authorized_email,
        commercial_profile=commercial_profile.strip(), created_at_utc=now, updated_at_utc=now,
    )
    db.add(row)
    db.flush()
    _audit(db, row, "created", actor)
    return row


def issue_token(db: Session, row: PilotEnrollment, *, actor: str, lifetime_hours: int = 72) -> str:
    if row.status not in {"PENDING", "APPROVED", "EXPIRED"}:
        raise EnrollmentRejected("Enrollment cannot issue a new token in this state.")
    if not 1 <= lifetime_hours <= 168:
        raise EnrollmentRejected("Token lifetime must be 1 to 168 hours.")
    token = "bcs_enr_" + secrets.token_urlsafe(48)
    row.token_hash = _hash(token)
    row.token_expires_at_utc = utc_now() + timedelta(hours=lifetime_hours)
    row.status = "APPROVED"
    row.updated_at_utc = utc_now()
    db.flush()
    _audit(db, row, "approved_or_reissued", actor)
    return token


def change_status(db: Session, row: PilotEnrollment, *, action: str, actor: str) -> None:
    transitions = {
        "revoke": ({"PENDING", "APPROVED", "EXPIRED", "SUSPENDED"}, "REVOKED"),
        "suspend": ({"REGISTERED", "ACTIVE"}, "SUSPENDED"),
        "activate": ({"REGISTERED", "SUSPENDED"}, "ACTIVE"),
        "expire": ({"APPROVED"}, "EXPIRED"),
    }
    if action not in transitions or row.status not in transitions[action][0]:
        raise EnrollmentRejected("Enrollment transition is not permitted.")
    row.status = transitions[action][1]
    row.token_hash = None
    row.updated_at_utc = utc_now()
    db.flush()
    _audit(db, row, action, actor)


def claim_enrollment(db: Session, *, token: str, identity_key: str,
                     authorized_email: str) -> int:
    """Atomically reserve one code within the caller's registration transaction.

    Caller MUST commit together with registration; on failure caller rolls back.
    Conditional UPDATE prevents concurrent one-use replay even with SQLite.
    """
    if not token.startswith("bcs_enr_") or len(token) > 128:
        raise EnrollmentRejected("Pilot enrollment authorization failed.")
    key = _hash(token)
    now = utc_now()
    result = db.execute(
        update(PilotEnrollment)
        .where(
            PilotEnrollment.token_hash == key,
            PilotEnrollment.status == "APPROVED",
            PilotEnrollment.identity_key == identity_key,
            PilotEnrollment.authorized_email == authorized_email.strip().lower(),
            PilotEnrollment.token_expires_at_utc > now,
            PilotEnrollment.registered_tenant_id.is_(None),
        )
        .values(status="REGISTERED", token_hash=None, registered_at_utc=now, updated_at_utc=now)
    )
    if result.rowcount != 1:
        raise EnrollmentRejected("Pilot enrollment authorization failed.")
    row = db.scalar(select(PilotEnrollment).where(
        PilotEnrollment.identity_key == identity_key,
        PilotEnrollment.status == "REGISTERED",
        PilotEnrollment.registered_at_utc == now,
    ))
    if row is None:
        raise EnrollmentRejected("Pilot enrollment reservation could not be loaded.")
    _audit(db, row, "registered", "bc-registration")
    return row.id


def bind_registered_tenant(db: Session, *, enrollment_id: int, tenant_id: str) -> None:
    result = db.execute(
        update(PilotEnrollment)
        .where(PilotEnrollment.id == enrollment_id,
               PilotEnrollment.status == "REGISTERED",
               PilotEnrollment.registered_tenant_id.is_(None))
        .values(registered_tenant_id=tenant_id, updated_at_utc=utc_now())
    )
    if result.rowcount != 1:
        raise EnrollmentRejected("Pilot enrollment tenant binding failed.")
