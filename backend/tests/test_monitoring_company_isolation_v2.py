from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, Tenant
from app.services.monitoring_report_service import _load_scans


COMPANY_A = "11111111-2222-3333-4444-555555555555"
COMPANY_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def test_v2_monitoring_history_filters_company_before_limit(monkeypatch, tenant_factory, scan_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant_id = tenant_factory()["tenant_id"]
    other_tenant = tenant_factory()["tenant_id"]
    ids = ["company-a-old"] + [f"company-b-{i}" for i in range(13)] + ["company-a-current", "other-tenant"]
    for scan_id in ids:
        scan_factory(tenant_id=other_tenant if scan_id == "other-tenant" else tenant_id, scan_id=scan_id)
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant.bc_company_id = COMPANY_A
        now = datetime.now(timezone.utc)
        for index, scan_id in enumerate(ids):
            scan = db.scalar(select(Scan).where(Scan.scan_id == scan_id))
            scan.bc_company_id = COMPANY_B if scan_id.startswith("company-b-") else "{" + COMPANY_A.upper() + "}"
            scan.generated_at_utc = now + timedelta(seconds=index)
        db.commit()
        assert [scan.scan_id for scan in _load_scans(db, tenant, "company-a-current")] == ["company-a-old", "company-a-current"]
        with pytest.raises(HTTPException) as error:
            _load_scans(db, tenant, "company-b-0")
        assert error.value.status_code == 404
        tenant.bc_company_id = None
        with pytest.raises(HTTPException) as error:
            _load_scans(db, tenant, "company-a-current")
        assert error.value.status_code == 409


def test_legacy_monitoring_history_contract_unchanged(monkeypatch, tenant_factory, scan_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", False)
    tenant_id = tenant_factory()["tenant_id"]
    scan_factory(tenant_id=tenant_id, scan_id="legacy-monitoring-history")
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
        assert [scan.scan_id for scan in _load_scans(db, tenant, "legacy-monitoring-history")] == ["legacy-monitoring-history"]
