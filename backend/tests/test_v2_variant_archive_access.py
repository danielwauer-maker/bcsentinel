"""Authenticated v2 archived report links are one-use and strictly variant scoped."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets

import pytest

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, Tenant, TenantProductEntitlement
from app.report_archive_models import ReportAccessGrant, ReportArchive

COMPANY = "11111111-2222-3333-4444-555555555555"
SCAN = "v2-variant-link-test-scan"


@pytest.fixture(autouse=True)
def v2_enabled(monkeypatch):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)


def _seed(tenant_factory, scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    scan_factory(tenant_id=tenant["tenant_id"], scan_id=SCAN)
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        owner = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        owner.premium_until_utc = now + timedelta(days=14)
        scan = db.query(Scan).filter_by(scan_id=SCAN).one()
        scan.bc_company_id = COMPANY
        scan.lcy_code = "EUR"
        db.add(TenantProductEntitlement(
            tenant_id=tenant["tenant_id"], product_code="full_assessment_v2",
            source="test-grant", status="active", valid_until_utc=now + timedelta(days=14),
            created_at_utc=now, updated_at_utc=now,
        ))
        db.commit()
    return tenant


def _issue_archived_grant(tenant_id, *, variant="validation"):
    raw_code = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    envelope = {
        "contract_version": "bcsentinel-render-bridge-v1",
        "source": "live", "status": "ready", "variant": variant,
        "tenant_id": tenant_id, "company_id": COMPANY, "scan_id": SCAN,
        "language": "en",
        "currency": {
            "source_currency": "EUR", "company_lcy_code": "EUR",
            "report_currency": "EUR", "model_currency_provenance": "eur_model",
            "conversion_status": "not_required", "fx_snapshot_id": None,
        },
        "report": {"evidence": "unit-test-only"}, "render_vm": None,
    }
    payload = json.dumps(envelope, sort_keys=True, separators=(",", ":"))
    with SessionLocal() as db:
        db.add(ReportArchive(
            tenant_id=tenant_id, company_id=COMPANY, scan_id=SCAN,
            variant=variant, contract_version=envelope["contract_version"],
            payload_json=payload,
            sha256=hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            created_at_utc=now,
        ))
        db.add(ReportAccessGrant(
            token_hash=hashlib.sha256(raw_code.encode()).hexdigest(),
            tenant_id=tenant_id, company_id=COMPANY, scan_id=SCAN,
            variant=variant, created_at_utc=now,
            expires_at_utc=now + timedelta(seconds=60),
        ))
        db.commit()
    return raw_code


def test_validation_report_one_use_link_redeems_and_scope_is_restricted(
    client, tenant_factory, scan_factory,
):
    tenant = _seed(tenant_factory, scan_factory)
    code = _issue_archived_grant(tenant["tenant_id"])
    data = {"code": code, "scan_id": SCAN, "company_id": COMPANY, "report_variant": "validation"}
    first = client.post("/reports/access/exchange", json=data)
    assert first.status_code == 200, first.text
    grant = first.json()
    assert grant["report_variant"] == "validation"
    assert grant["tenant_id"] == tenant["tenant_id"]
    assert client.post("/reports/access/exchange", json=data).status_code == 403
    headers = {"Authorization": "Bearer " + grant["access_token"]}
    good = client.get(
        f"/account/reports/validation/{SCAN}", params={"company_id": COMPANY}, headers=headers
    )
    assert good.status_code == 200, good.text
    assert good.json()["variant"] == "validation"
    assert client.get(
        f"/account/reports/full/{SCAN}", params={"company_id": COMPANY}, headers=headers
    ).status_code in {401, 403}
    assert client.get(
        f"/account/reports/validation/{SCAN}",
        params={"company_id": "aaaaaaaa-2222-3333-4444-555555555555"}, headers=headers
    ).status_code in {401, 403, 404}


def test_one_use_exchange_rejects_requested_variant_mismatch(
    client, tenant_factory, scan_factory,
):
    tenant = _seed(tenant_factory, scan_factory)
    code = _issue_archived_grant(tenant["tenant_id"])
    res = client.post("/reports/access/exchange", json={
        "code": code, "scan_id": SCAN, "company_id": COMPANY,
        "report_variant": "monitoring",
    })
    assert res.status_code == 403


def test_expired_v2_access_blocks_previously_issued_report_code(
    client, tenant_factory, scan_factory,
):
    tenant = _seed(tenant_factory, scan_factory)
    code = _issue_archived_grant(tenant["tenant_id"])
    with SessionLocal() as db:
        owner = db.query(Tenant).filter_by(tenant_id=tenant["tenant_id"]).one()
        owner.premium_until_utc = datetime.now(timezone.utc) - timedelta(days=1)
        for entitlement in db.query(TenantProductEntitlement).filter_by(tenant_id=tenant["tenant_id"]):
            entitlement.valid_until_utc = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
    res = client.post("/reports/access/exchange", json={
        "code": code, "scan_id": SCAN, "company_id": COMPANY,
        "report_variant": "validation",
    })
    assert res.status_code == 403
