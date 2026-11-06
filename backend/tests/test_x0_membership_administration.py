from __future__ import annotations

from datetime import timedelta

import pytest

from app.account_models import TenantInvitation, TenantMembership
from app.db import SessionLocal
from app.services.account_membership_service import get_or_create_user_identity, upsert_tenant_membership
from app.services.tenant_membership_admin_service import (
    accept_invitation,
    change_member_role,
    create_invitation,
    revoke_invitation,
    revoke_member,
    utc_now,
)


def _seed_admin(tenant_id: str, subject: str = "admin-subject", email: str = "admin@example.com") -> int:
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject=subject,
            email=email,
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_id,
            role="ADMIN",
            status="active",
        )
        db.commit()
        return user.id


def test_invitation_token_is_hashed_and_verified_email_can_accept(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        invitation, raw = create_invitation(
            db,
            tenant_id=tenant["tenant_id"],
            email="Invitee@Example.com",
            role="VIEWER",
            actor_user_identity_id=admin_id,
        )
        invitation_id = invitation.id
        assert raw not in invitation.token_hash
        db.commit()

    with SessionLocal() as db:
        invitee = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="invitee-subject",
            email="invitee@example.com",
        )
        membership = accept_invitation(db, raw_token=raw, user=invitee)
        db.commit()
        assert membership.tenant_id == tenant["tenant_id"]
        assert membership.role == "VIEWER"
        accepted = db.get(TenantInvitation, invitation_id)
        assert accepted.status == "accepted"


def test_invitation_cannot_be_accepted_by_different_verified_email(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        _, raw = create_invitation(
            db,
            tenant_id=tenant["tenant_id"],
            email="right@example.com",
            role="SETUP",
            actor_user_identity_id=admin_id,
        )
        db.commit()

    with SessionLocal() as db:
        wrong = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="wrong-subject",
            email="wrong@example.com",
        )
        with pytest.raises(Exception) as exc:
            accept_invitation(db, raw_token=raw, user=wrong)
        assert getattr(exc.value, "status_code", None) == 403


def test_invitation_can_be_revoked(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        invitation, _ = create_invitation(
            db,
            tenant_id=tenant["tenant_id"],
            email="revoke@example.com",
            role="VIEWER",
            actor_user_identity_id=admin_id,
        )
        invitation_id = invitation.id
        revoke_invitation(db, invitation_id=invitation_id, actor_user_identity_id=admin_id)
        db.commit()
        assert db.get(TenantInvitation, invitation_id).status == "revoked"


def test_last_admin_cannot_be_demoted_or_revoked(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        admin_membership = db.query(TenantMembership).filter_by(
            tenant_id=tenant["tenant_id"], user_identity_id=admin_id
        ).one()
        with pytest.raises(ValueError, match="last active tenant ADMIN"):
            change_member_role(
                db,
                tenant_id=tenant["tenant_id"],
                membership_id=admin_membership.id,
                role="VIEWER",
                actor_user_identity_id=admin_id,
            )
        with pytest.raises(ValueError, match="last active tenant ADMIN"):
            revoke_member(
                db,
                tenant_id=tenant["tenant_id"],
                membership_id=admin_membership.id,
                actor_user_identity_id=admin_id,
            )


def test_role_change_invalidates_membership_binding_timestamp(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        member = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="member-subject",
            email="member@example.com",
        )
        membership = upsert_tenant_membership(
            db,
            user_identity_id=member.id,
            tenant_id=tenant["tenant_id"],
            role="VIEWER",
            status="active",
        )
        old_updated = membership.updated_at_utc
        changed = change_member_role(
            db,
            tenant_id=tenant["tenant_id"],
            membership_id=membership.id,
            role="SETUP",
            actor_user_identity_id=admin_id,
        )
        assert changed.role == "SETUP"
        assert changed.updated_at_utc >= old_updated


def test_expired_invitation_is_rejected(tenant_factory):
    tenant = tenant_factory()
    admin_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        invitation, raw = create_invitation(
            db,
            tenant_id=tenant["tenant_id"],
            email="expired@example.com",
            role="VIEWER",
            actor_user_identity_id=admin_id,
        )
        invitation.expires_at_utc = utc_now() - timedelta(seconds=1)
        db.commit()

    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="expired-subject",
            email="expired@example.com",
        )
        with pytest.raises(Exception) as exc:
            accept_invitation(db, raw_token=raw, user=user)
        assert getattr(exc.value, "status_code", None) == 410
