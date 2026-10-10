from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func, select

from app.account_models import TenantInvitation, TenantMembership, UserIdentity
from app.models import AdminAuditEvent, Tenant
from app.services.account_membership_service import normalize_email, normalize_role

INVITATION_TTL_HOURS = 72


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _audit(db, *, actor_user_id: int, action: str, target_type: str, target_id: str, details: dict) -> None:
    db.add(
        AdminAuditEvent(
            admin_username=f"user:{actor_user_id}",
            action=action[:80],
            target_type=target_type[:60],
            target_id=str(target_id)[:120],
            details_json=json.dumps(details, sort_keys=True, default=str),
            created_at_utc=utc_now(),
        )
    )


def require_tenant_admin(db, *, user_identity_id: int, tenant_id: str) -> TenantMembership:
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_identity_id == user_identity_id,
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.status == "active",
        )
    )
    if membership is None or membership.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Tenant ADMIN role is required.")
    return membership


def create_invitation(
    db,
    *,
    tenant_id: str,
    email: str,
    role: str,
    actor_user_identity_id: int,
    ttl_hours: int = INVITATION_TTL_HOURS,
) -> tuple[TenantInvitation, str]:
    require_tenant_admin(db, user_identity_id=actor_user_identity_id, tenant_id=tenant_id)
    if db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id)) is None:
        raise ValueError("Tenant not found.")
    normalized_email = normalize_email(email)
    if not normalized_email or "@" not in normalized_email:
        raise ValueError("A valid invitation email is required.")
    normalized_role = normalize_role(role)
    existing_user_ids = db.scalars(
        select(UserIdentity.id).where(UserIdentity.email_normalized == normalized_email)
    ).all()
    if existing_user_ids:
        existing_membership = db.scalar(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_identity_id.in_(existing_user_ids),
                TenantMembership.status == "active",
            )
        )
        if existing_membership is not None:
            raise ValueError("This email already has an active tenant membership.")

    now = utc_now()
    pending = db.scalars(
        select(TenantInvitation).where(
            TenantInvitation.tenant_id == tenant_id,
            TenantInvitation.email_normalized == normalized_email,
            TenantInvitation.status == "pending",
        )
    ).all()
    for invitation in pending:
        if invitation.expires_at_utc > now:
            raise ValueError("An active invitation already exists for this email and tenant.")
        invitation.status = "expired"

    raw_token = secrets.token_urlsafe(32)
    invitation = TenantInvitation(
        tenant_id=tenant_id,
        email_normalized=normalized_email,
        role=normalized_role,
        token_hash=_token_hash(raw_token),
        status="pending",
        expires_at_utc=now + timedelta(hours=max(1, int(ttl_hours))),
        invited_by_user_identity_id=actor_user_identity_id,
        created_at_utc=now,
    )
    db.add(invitation)
    db.flush()
    _audit(
        db,
        actor_user_id=actor_user_identity_id,
        action="tenant_invitation.create",
        target_type="tenant_invitation",
        target_id=str(invitation.id),
        details={"tenant_id": tenant_id, "email": normalized_email, "role": normalized_role},
    )
    return invitation, raw_token


def accept_invitation(db, *, raw_token: str, user: UserIdentity) -> TenantMembership:
    invitation = db.scalar(
        select(TenantInvitation).where(TenantInvitation.token_hash == _token_hash((raw_token or "").strip()))
    )
    now = utc_now()
    if invitation is None or invitation.status != "pending":
        raise HTTPException(status_code=404, detail="Invitation is invalid or no longer available.")
    if invitation.expires_at_utc <= now:
        invitation.status = "expired"
        db.flush()
        raise HTTPException(status_code=410, detail="Invitation has expired.")
    if normalize_email(user.email_normalized) != invitation.email_normalized:
        raise HTTPException(status_code=403, detail="Invitation belongs to a different verified email address.")

    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_identity_id == user.id,
            TenantMembership.tenant_id == invitation.tenant_id,
        )
    )
    if membership is None:
        membership = TenantMembership(
            user_identity_id=user.id,
            tenant_id=invitation.tenant_id,
            role=invitation.role,
            status="active",
            invited_email_normalized=invitation.email_normalized,
            invited_by=f"user:{invitation.invited_by_user_identity_id}",
            invited_at_utc=invitation.created_at_utc,
            accepted_at_utc=now,
            created_at_utc=now,
            updated_at_utc=now,
        )
        db.add(membership)
    else:
        membership.role = invitation.role
        membership.status = "active"
        membership.accepted_at_utc = now
        membership.revoked_at_utc = None
        membership.updated_at_utc = now
    invitation.status = "accepted"
    invitation.accepted_by_user_identity_id = user.id
    invitation.accepted_at_utc = now
    db.flush()
    _audit(
        db,
        actor_user_id=user.id,
        action="tenant_invitation.accept",
        target_type="tenant_membership",
        target_id=str(membership.id),
        details={"tenant_id": invitation.tenant_id, "role": membership.role, "invitation_id": invitation.id},
    )
    return membership


def revoke_invitation(db, *, invitation_id: int, actor_user_identity_id: int) -> TenantInvitation:
    invitation = db.get(TenantInvitation, invitation_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    require_tenant_admin(db, user_identity_id=actor_user_identity_id, tenant_id=invitation.tenant_id)
    if invitation.status != "pending":
        raise ValueError("Only pending invitations can be revoked.")
    invitation.status = "revoked"
    invitation.revoked_at_utc = utc_now()
    _audit(
        db,
        actor_user_id=actor_user_identity_id,
        action="tenant_invitation.revoke",
        target_type="tenant_invitation",
        target_id=str(invitation.id),
        details={"tenant_id": invitation.tenant_id, "email": invitation.email_normalized},
    )
    return invitation


def list_members(db, *, tenant_id: str, actor_user_identity_id: int) -> list[dict]:
    require_tenant_admin(db, user_identity_id=actor_user_identity_id, tenant_id=tenant_id)
    memberships = db.scalars(
        select(TenantMembership).where(TenantMembership.tenant_id == tenant_id).order_by(TenantMembership.id.asc())
    ).all()
    result = []
    for membership in memberships:
        user = db.get(UserIdentity, membership.user_identity_id)
        result.append(
            {
                "membership_id": membership.id,
                "user_identity_id": membership.user_identity_id,
                "email": user.email_normalized if user else None,
                "display_name": user.display_name if user else None,
                "role": membership.role,
                "status": membership.status,
                "accepted_at_utc": membership.accepted_at_utc,
            }
        )
    return result


def _active_admin_count(db, tenant_id: str) -> int:
    return int(
        db.scalar(
            select(func.count(TenantMembership.id)).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.status == "active",
                TenantMembership.role == "ADMIN",
            )
        )
        or 0
    )


def change_member_role(
    db,
    *,
    tenant_id: str,
    membership_id: int,
    role: str,
    actor_user_identity_id: int,
) -> TenantMembership:
    require_tenant_admin(db, user_identity_id=actor_user_identity_id, tenant_id=tenant_id)
    membership = db.get(TenantMembership, membership_id)
    if membership is None or membership.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Tenant member not found.")
    new_role = normalize_role(role)
    if membership.status != "active":
        raise ValueError("Only active members can change role.")
    if membership.role == "ADMIN" and new_role != "ADMIN" and _active_admin_count(db, tenant_id) <= 1:
        raise ValueError("The last active tenant ADMIN cannot be demoted.")
    old_role = membership.role
    membership.role = new_role
    membership.updated_at_utc = utc_now()
    _audit(
        db,
        actor_user_id=actor_user_identity_id,
        action="tenant_membership.role_change",
        target_type="tenant_membership",
        target_id=str(membership.id),
        details={"tenant_id": tenant_id, "old_role": old_role, "new_role": new_role},
    )
    return membership


def revoke_member(
    db,
    *,
    tenant_id: str,
    membership_id: int,
    actor_user_identity_id: int,
) -> TenantMembership:
    require_tenant_admin(db, user_identity_id=actor_user_identity_id, tenant_id=tenant_id)
    membership = db.get(TenantMembership, membership_id)
    if membership is None or membership.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Tenant member not found.")
    if membership.status != "active":
        raise ValueError("Only active members can be revoked.")
    if membership.role == "ADMIN" and _active_admin_count(db, tenant_id) <= 1:
        raise ValueError("The last active tenant ADMIN cannot be revoked.")
    membership.status = "revoked"
    membership.revoked_at_utc = utc_now()
    membership.updated_at_utc = membership.revoked_at_utc
    _audit(
        db,
        actor_user_id=actor_user_identity_id,
        action="tenant_membership.revoke",
        target_type="tenant_membership",
        target_id=str(membership.id),
        details={"tenant_id": tenant_id, "role": membership.role},
    )
    return membership
