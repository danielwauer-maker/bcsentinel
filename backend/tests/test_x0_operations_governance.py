from __future__ import annotations

from datetime import timedelta

from app.db import SessionLocal
from app.services.account_membership_service import get_or_create_user_identity, upsert_tenant_membership
from app.services.operations_governance_service import (
    create_data_lifecycle_request,
    feature_enabled,
    grant_diagnostics_support,
    record_telemetry,
    retention_policy,
    revoke_support_grant,
    set_feature_flag,
    support_diagnostics_active,
    utc_now,
)


def _seed_admin(tenant_id: str) -> int:
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject=f"ops-{tenant_id}",
            email=f"ops-{tenant_id}@example.com",
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


def test_support_access_is_diagnostics_only_and_time_limited(tenant_factory):
    tenant = tenant_factory()
    user_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        grant = grant_diagnostics_support(
            db,
            tenant_id=tenant["tenant_id"],
            user_identity_id=user_id,
            hours=24,
            reason="Pilot troubleshooting",
        )
        grant_id = grant.id
        assert grant.access_mode == "diagnostics"
        assert grant.valid_until_utc > grant.valid_from_utc
        assert support_diagnostics_active(db, tenant["tenant_id"]) is True
        revoke_support_grant(db, grant_id=grant_id, user_identity_id=user_id)
        db.commit()
        assert support_diagnostics_active(db, tenant["tenant_id"]) is False


def test_feature_flags_are_tenant_scoped(tenant_factory):
    tenant_a = tenant_factory()
    tenant_b = tenant_factory()
    with SessionLocal() as db:
        set_feature_flag(db, tenant_id=tenant_a["tenant_id"], flag_key="financial-preview", enabled=True, actor="pytest")
        db.commit()
        assert feature_enabled(db, tenant_id=tenant_a["tenant_id"], flag_key="financial-preview") is True
        assert feature_enabled(db, tenant_id=tenant_b["tenant_id"], flag_key="financial-preview") is False


def test_duplicate_pending_data_lifecycle_request_is_rejected(tenant_factory):
    tenant = tenant_factory()
    user_id = _seed_admin(tenant["tenant_id"])
    with SessionLocal() as db:
        create_data_lifecycle_request(db, tenant_id=tenant["tenant_id"], request_type="delete", user_identity_id=user_id)
        db.flush()
        try:
            create_data_lifecycle_request(db, tenant_id=tenant["tenant_id"], request_type="delete", user_identity_id=user_id)
            raised = False
        except ValueError:
            raised = True
        assert raised is True


def test_telemetry_drops_sensitive_metadata_keys(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        event = record_telemetry(
            db,
            event_name="scan.completed",
            outcome="success",
            tenant_id=tenant["tenant_id"],
            duration_ms=1234,
            metadata={"module_count": 4, "email": "secret@example.com", "token": "secret"},
        )
        assert "module_count" in event.metadata_json
        assert "secret@example.com" not in event.metadata_json
        assert "secret" not in event.metadata_json


def test_retention_policy_is_machine_readable():
    policy = retention_policy()
    assert policy["schema_version"] == "1.0.0"
    assert policy["export_before_delete_supported"] is True
    assert policy["security_audit_days"] >= policy["scan_history_days"]
