from __future__ import annotations

import pytest

from app.db import SessionLocal
from app.services.account_membership_service import (
    get_or_create_user_identity,
    list_active_memberships,
    require_active_membership,
    upsert_tenant_membership,
)
from app.services.tenant_access_service import set_tenant_status


def test_one_identity_can_access_multiple_tenants_with_independent_roles(tenant_factory):
    tenant_a = tenant_factory()
    tenant_b = tenant_factory()

    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="user-123",
            email="Pilot.User@Example.com",
            display_name="Pilot User",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_a["tenant_id"],
            role="ADMIN",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant_b["tenant_id"],
            role="VIEWER",
        )
        db.commit()
        user_id = user.id

    with SessionLocal() as db:
        memberships = list_active_memberships(db, user_id)

    assert [item["tenant_id"] for item in memberships] == sorted(
        [tenant_a["tenant_id"], tenant_b["tenant_id"]]
    )
    role_by_tenant = {item["tenant_id"]: item["role"] for item in memberships}
    assert role_by_tenant[tenant_a["tenant_id"]] == "ADMIN"
    assert role_by_tenant[tenant_b["tenant_id"]] == "VIEWER"


def test_same_email_does_not_collapse_distinct_provider_subjects(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        first = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="subject-a",
            email="shared@example.com",
        )
        second = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="subject-b",
            email="shared@example.com",
        )
        upsert_tenant_membership(
            db,
            user_identity_id=first.id,
            tenant_id=tenant["tenant_id"],
            role="ADMIN",
        )
        db.commit()
        assert first.id != second.id


def test_suspended_tenant_is_hidden_from_active_membership_selection(tenant_factory):
    tenant_a = tenant_factory()
    tenant_b = tenant_factory()

    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="user-suspended-test",
            email="user@example.com",
        )
        upsert_tenant_membership(db, user_identity_id=user.id, tenant_id=tenant_a["tenant_id"], role="ADMIN")
        upsert_tenant_membership(db, user_identity_id=user.id, tenant_id=tenant_b["tenant_id"], role="ADMIN")
        set_tenant_status(
            db,
            tenant_id=tenant_b["tenant_id"],
            status="suspended",
            reason="x0 test",
            updated_by="pytest",
        )
        db.commit()
        user_id = user.id

    with SessionLocal() as db:
        memberships = list_active_memberships(db, user_id)

    assert [item["tenant_id"] for item in memberships] == [tenant_a["tenant_id"]]


def test_revoked_membership_cannot_be_selected(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="revoked-user",
            email="revoked@example.com",
        )
        membership = upsert_tenant_membership(
            db,
            user_identity_id=user.id,
            tenant_id=tenant["tenant_id"],
            role="VIEWER",
            status="revoked",
        )
        db.commit()
        user_id = user.id
        assert membership.status == "revoked"

    with SessionLocal() as db:
        assert list_active_memberships(db, user_id) == []
        with pytest.raises(Exception) as exc:
            require_active_membership(db, user_identity_id=user_id, tenant_id=tenant["tenant_id"])
        assert getattr(exc.value, "status_code", None) == 403


def test_membership_role_validation_rejects_unknown_role(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-idp",
            provider_subject="bad-role-user",
            email="role@example.com",
        )
        with pytest.raises(ValueError):
            upsert_tenant_membership(
                db,
                user_identity_id=user.id,
                tenant_id=tenant["tenant_id"],
                role="SUPERUSER",
            )
