import pytest
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import SandboxQAScanGrant, Tenant
from app.services.qa_environment_service import is_sandbox_qa_dev_environment, require_sandbox_qa_dev_environment
from app.services.sandbox_qa_scan_service import claim_grant, issue_grant
from app.services.atomic_scan_start_service import _resolve_access_and_credit


def test_sandbox_qa_environment_allows_only_explicit_dev(monkeypatch):
    monkeypatch.setattr(settings, "ENV", "dev")
    assert is_sandbox_qa_dev_environment()
    require_sandbox_qa_dev_environment()


@pytest.mark.parametrize("environment", [None, "", "prod", "production", "staging", "test", "DEV", " dev ", "unknown"])
def test_sandbox_qa_environment_is_fail_closed(monkeypatch, environment):
    monkeypatch.setattr(settings, "ENV", environment)
    assert not is_sandbox_qa_dev_environment()
    with pytest.raises(ValueError, match="explicitly configured as dev"):
        require_sandbox_qa_dev_environment()


@pytest.mark.parametrize("environment", [None, "", "prod", "production", "staging", "test", "unknown"])
def test_denied_environment_cannot_issue_or_consume_a_qa_grant(monkeypatch, tenant_factory, environment):
    tenant_info = tenant_factory()
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_info["tenant_id"]))
        tenant.bc_environment_type = "sandbox"
        tenant.bc_environment_name = "Sandbox"
        tenant.bc_company_id = "company-id"
        db.commit()

        monkeypatch.setattr(settings, "ENV", environment)
        with pytest.raises(ValueError, match="explicitly configured as dev"):
            issue_grant(db, tenant=tenant, company_id="company-id", environment_name="Sandbox",
                        issued_by="operator", expires_in_minutes=30)
        assert db.scalar(select(SandboxQAScanGrant.id)) is None

        # A previously issued DEV grant remains untouched when a later start
        # is attempted from a denied environment.
        monkeypatch.setattr(settings, "ENV", "dev")
        grant = issue_grant(db, tenant=tenant, company_id="company-id", environment_name="Sandbox",
                            issued_by="operator", expires_in_minutes=30)
        db.commit()
        monkeypatch.setattr(settings, "ENV", environment)
        with pytest.raises(ValueError, match="explicitly configured as dev"):
            claim_grant(db, tenant=tenant, company_id="company-id", environment_name="Sandbox", scan_id="qa-scan")
        db.rollback()
        assert db.get(SandboxQAScanGrant, grant.id).status == "available"


def test_atomic_start_path_fails_before_consuming_in_denied_environment(monkeypatch, tenant_factory):
    tenant_info = tenant_factory()
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_info["tenant_id"]))
        tenant.bc_environment_type = "sandbox"
        tenant.bc_environment_name = "Sandbox"
        tenant.bc_company_id = "company-id"
        monkeypatch.setattr(settings, "ENV", "dev")
        grant = issue_grant(db, tenant=tenant, company_id="company-id", environment_name="Sandbox",
                            issued_by="operator", expires_in_minutes=30)
        db.commit()
        monkeypatch.setattr(settings, "ENV", "production")
        with pytest.raises(ValueError, match="explicitly configured as dev"):
            _resolve_access_and_credit(
                db, tenant=tenant, requested_mode="sandbox_qa", scan_id="qa-scan",
                expectation_company="company-id", expectation_environment="Sandbox",
            )
        db.rollback()
        assert db.get(SandboxQAScanGrant, grant.id).status == "available"
