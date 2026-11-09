from sqlalchemy import select

from app.models import DashboardUserTenantMembership, Tenant, TenantScanCredit
from app.services.tenant_registration_service import (
    RegistrationAuthenticationError,
    build_registration_identity,
    upsert_tenant_registration,
)

import pytest


def test_existing_identity_requires_tenant_credentials(db_session):
    identity = build_registration_identity(
        entra_tenant_id="11111111-1111-1111-1111-111111111111",
        environment_name="sandbox", environment_type="sandbox",
        company_id="22222222-2222-2222-2222-222222222222", company_name="Test",
    )
    args = dict(identity=identity, app_version="1.0.2.55", contact_email="first@example.com", preferred_language="en")
    created = upsert_tenant_registration(db_session, **args)
    tenant = db_session.scalar(select(Tenant).where(Tenant.tenant_id == created.tenant_id))
    credits_before = len(db_session.scalars(select(TenantScanCredit).where(TenantScanCredit.tenant_id == tenant.tenant_id)).all())
    with pytest.raises(RegistrationAuthenticationError):
        upsert_tenant_registration(db_session, **{**args, "contact_email": "other@example.com"})
    assert tenant.contact_email == "first@example.com"
    assert len(db_session.scalars(select(DashboardUserTenantMembership).where(DashboardUserTenantMembership.tenant_id == tenant.tenant_id)).all()) == 1
    resumed = upsert_tenant_registration(
        db_session, **args, existing_tenant_id=created.tenant_id,
        header_tenant_id=created.tenant_id, header_api_token=created.api_token,
    )
    assert resumed.api_token == created.api_token
    assert len(db_session.scalars(select(TenantScanCredit).where(TenantScanCredit.tenant_id == tenant.tenant_id)).all()) == credits_before


def test_concurrent_first_registration_has_one_winner():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.db import SessionLocal, engine

    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrent registration requires PostgreSQL row and uniqueness semantics")
    identity = build_registration_identity(
        entra_tenant_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        environment_name="Concurrent", environment_type="sandbox",
        company_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", company_name="Test",
    )
    barrier = Barrier(2)

    def register():
        with SessionLocal() as db:
            barrier.wait(timeout=10)
            try:
                result = upsert_tenant_registration(
                    db, identity=identity, app_version="1.0.2.55",
                    contact_email="first@example.com", preferred_language="en",
                )
                return result.registration_status
            except RegistrationAuthenticationError:
                db.rollback()
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: register(), range(2)))
    assert sorted(outcomes) == ["created", "rejected"]
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.registration_identity_key == identity.key))
        assert tenant is not None
        assert len(db.scalars(select(Tenant).where(Tenant.registration_identity_key == identity.key)).all()) == 1
        assert len(db.scalars(select(TenantScanCredit).where(TenantScanCredit.tenant_id == tenant.tenant_id)).all()) <= 1
