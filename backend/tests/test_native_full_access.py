"""Integration regression for BC-native Full report access and history.

No OIDC, BC API token stays server-side. All browser tokens are scoped to one
tenant/company/scan and all exchange codes are one-time.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan, ScanRunStatus, Tenant, TenantScanCredit
from app.report_archive_models import ReportAccessGrant, ReportArchive
from app.services.report_archive_service import issue_full_link, redeem_code, verify_scoped_session
from app.routers.report_render_data import ReportRenderEnvelope

COMPANY = "11111111-2222-3333-4444-555555555555"
OTHER = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SCAN = "native_archived_scan"


def _seed(tenant_factory, scan_factory):
    t = tenant_factory()
    scan_factory(tenant_id=t["tenant_id"], scan_id=SCAN)
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == SCAN).one()
        scan.bc_company_id = COMPANY
        scan.lcy_code = "EUR"
        db.query(Tenant).filter_by(tenant_id=t["tenant_id"]).one().bc_company_id = COMPANY
        envelope = ReportRenderEnvelope(
            variant="full", tenant_id=t["tenant_id"], company_id=COMPANY,
            scan_id=SCAN, language="de",
            currency={"source_currency": "EUR", "company_lcy_code": "EUR",
                      "report_currency": "EUR", "model_currency_provenance": "eur_model",
                      "conversion_status": "not_required", "fx_snapshot_id": None},
            report={"scan_id": SCAN, "tenant_id": t["tenant_id"]},
            render_vm={"basis": "scan_evidence", "kind": "full"},
        )
        value = json.dumps(envelope.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        db.add(ReportArchive(
            tenant_id=t["tenant_id"], company_id=COMPANY, scan_id=SCAN,
            variant="full", contract_version="bcsentinel-render-bridge-v1",
            payload_json=value, sha256=hashlib.sha256(value.encode()).hexdigest(),
            created_at_utc=datetime.now(timezone.utc),
        ))
        db.commit()
    return t


def _activate_full(tenant_id: str, *, hours: int = 2) -> None:
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).one()
        tenant.premium_until_utc = datetime.now(timezone.utc) + timedelta(hours=hours)
        db.commit()


def _record_scan_provenance(tenant_id: str, product: str | None, *, status="completed"):
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(ScanRunStatus(
            tenant_id=tenant_id, run_id=SCAN, status=status, company_name="Test Company",
            updated_at_utc=now, result_persisted_at_utc=now if status == "completed" else None,
        ))
        if product is not None:
            db.add(TenantScanCredit(
                tenant_id=tenant_id, product_code=product, status="consumed",
                consumed_scan_id=SCAN, created_at_utc=now, consumed_at_utc=now,
            ))
        db.commit()


@pytest.mark.parametrize(("product", "status", "reason"), [
    ("validation_check", "completed", "WRONG_REPORT_VARIANT"),
    ("free_entry", "running", "SCAN_NOT_COMPLETED"),
    (None, "completed", "FULL_BASELINE_NOT_VERIFIED"),
    ("free_entry", "completed", "ASSESSMENT_SCOPE_NOT_CONFIRMED"),
])
def test_v2_full_requires_completed_original_free_scan_with_confirmed_scope(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory,
    product, status, reason,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    tenant = _seed(tenant_factory, scan_factory)
    _activate_full(tenant["tenant_id"])
    _record_scan_provenance(tenant["tenant_id"], product, status=status)
    with SessionLocal() as db:
        db.query(ReportArchive).filter_by(scan_id=SCAN).delete()
        db.commit()
    response = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(tenant))
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == reason
    preflight = client.get(f"/scans/{SCAN}/report-preflight", headers=auth_header_factory(tenant))
    assert preflight.json()["full_report_reason"] == reason
    with SessionLocal() as db:
        assert db.query(ReportAccessGrant).filter_by(scan_id=SCAN).count() == 0
        assert db.query(ReportArchive).filter_by(scan_id=SCAN).count() == 0
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"]).count() == int(product is not None)


@pytest.mark.parametrize(("company", "lcy", "status", "reason"), [
    (None, "EUR", 409, "SCAN_COMPANY_NOT_VERIFIED"),
    ("invalid", "EUR", 409, "SCAN_COMPANY_NOT_VERIFIED"),
    (OTHER, "EUR", 404, "Report not found."),
    (COMPANY, None, 409, "SCAN_CURRENCY_NOT_VERIFIED"),
    (COMPANY, "USD", 409, "SCAN_CURRENCY_NOT_VERIFIED"),
])
def test_full_rechecks_company_and_currency_even_with_an_archive(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory,
    company, lcy, status, reason,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    tenant = _seed(tenant_factory, scan_factory)
    _activate_full(tenant["tenant_id"])
    _record_scan_provenance(tenant["tenant_id"], "free_entry")
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id=SCAN).one()
        scan.bc_company_id, scan.lcy_code = company, lcy
        db.commit()
    response = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(tenant))
    assert response.status_code == status, response.text
    assert response.json()["detail"] == reason


def test_v2_original_free_scan_can_create_and_reopen_immutable_archive(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory,
):
    from urllib.parse import parse_qs, urlsplit

    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    tenant = _seed(tenant_factory, scan_factory)
    _record_scan_provenance(tenant["tenant_id"], "free_entry")
    headers = auth_header_factory(tenant)
    url = f"/reports/executive/{SCAN}/v6-link"
    with SessionLocal() as db:
        db.query(ReportArchive).filter_by(scan_id=SCAN).delete()
        db.query(Scan).filter_by(scan_id=SCAN).one().bc_company_id = "{" + COMPANY + "}"
        db.commit()
    assert client.post(url, headers=headers).status_code == 402
    _activate_full(tenant["tenant_id"])
    scope = client.post(f"/scans/{SCAN}/assessment-scope/confirm", headers=headers, json={})
    assert scope.status_code == 200, scope.text
    first = client.post(url, headers=headers)
    assert first.status_code == 200, first.text
    query = parse_qs(urlsplit(first.json()["url"]).query)
    exchanged = client.post("/reports/access/exchange", json={
        "code": query["code"][0], "scan_id": SCAN, "company_id": COMPANY, "report_variant": "full",
    })
    assert exchanged.status_code == 200, exchanged.text
    rendered = client.get(
        f"/account/reports/full/{SCAN}", params={"company_id": COMPANY},
        headers={"Authorization": "Bearer " + exchanged.json()["access_token"]},
    )
    assert rendered.status_code == 200, rendered.text
    with SessionLocal() as db:
        archived = db.query(ReportArchive).filter_by(scan_id=SCAN).one()
        digest = archived.sha256
        assert json.loads(archived.payload_json)["render_vm"]["kind"] == "full"
    second = client.post(url, headers=headers)
    assert second.status_code == 200 and second.json()["url"] != first.json()["url"]
    with SessionLocal() as db:
        assert db.query(ReportArchive).filter_by(scan_id=SCAN).one().sha256 == digest
        assert db.query(TenantScanCredit).filter_by(tenant_id=tenant["tenant_id"]).count() == 1
        assert db.query(Scan).filter_by(scan_id=SCAN).one().bc_company_id == "{" + COMPANY + "}"
    foreign = tenant_factory()
    _activate_full(foreign["tenant_id"])
    assert client.post(url, headers=auth_header_factory(foreign)).status_code == 404


def test_archived_report_requires_active_access_and_code_is_one_use(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory, product_access_factory
):
    t = _seed(tenant_factory, scan_factory)
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", False)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    assert client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t)).status_code == 402
    product_access_factory(tenant_id=t["tenant_id"])
    issued = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t))
    assert issued.status_code == 200, issued.text
    from urllib.parse import urlparse, parse_qs
    url = issued.json()["url"]
    assert url.startswith("https://reports.example.test/report/live?")
    q = parse_qs(urlparse(url).query)
    assert q["scanId"] == [SCAN] and q["companyId"] == [COMPANY]
    assert t["api_token"] not in url
    body = {"code": q["code"][0], "scan_id": SCAN, "company_id": COMPANY, "report_variant": "full"}
    first = client.post("/reports/access/exchange", json=body)
    assert first.status_code == 200, first.text
    assert first.headers["cache-control"].startswith("no-store")
    data = first.json()
    assert data["report_variant"] == "full"
    assert data["tenant_id"] == t["tenant_id"]
    assert data["scan_id"] == SCAN
    assert data["company_id"] == COMPANY
    assert data["access_token"] not in url
    assert verify_scoped_session("Bearer " + data["access_token"], scan_id=SCAN, company_id=COMPANY, variant="full") == t["tenant_id"]
    assert verify_scoped_session("Bearer " + data["access_token"], scan_id="other_scan", company_id=COMPANY, variant="full") is None
    assert verify_scoped_session("Bearer " + data["access_token"], scan_id=SCAN, company_id=OTHER, variant="full") is None
    again = client.post("/reports/access/exchange", json=body)
    assert again.status_code == 403
    report = client.get(f"/account/reports/full/{SCAN}?company_id={COMPANY}", headers={"Authorization": "Bearer " + data["access_token"]})
    assert report.status_code == 200, report.text
    assert report.json()["render_vm"]["kind"] == "full"
    assert report.headers["cache-control"].startswith("no-store")
    denied = client.get(f"/account/reports/full/{SCAN}?company_id={OTHER}", headers={"Authorization": "Bearer " + data["access_token"]})
    assert denied.status_code in (401, 403, 404)


def test_expired_premium_cannot_issue_new_code_or_redeem_old_code(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    t = _seed(tenant_factory, scan_factory)
    _record_scan_provenance(t["tenant_id"], "free_entry")
    _activate_full(t["tenant_id"])
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    from urllib.parse import urlparse, parse_qs
    issued = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t))
    assert issued.status_code == 200, issued.text
    code = parse_qs(urlparse(issued.json()["url"]).query)["code"][0]
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == t["tenant_id"]).one()
        tenant.premium_until_utc = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
    body = {"code": code, "scan_id": SCAN, "company_id": COMPANY, "report_variant": "full"}
    assert client.post("/reports/access/exchange", json=body).status_code == 403
    assert client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t)).status_code == 402


def test_history_is_company_and_tenant_scoped(client, tenant_factory, scan_factory, auth_header_factory):
    t = _seed(tenant_factory, scan_factory)
    found = client.get(f"/reports/access/history?company_id={COMPANY}", headers=auth_header_factory(t))
    assert found.status_code == 200, found.text
    assert [r["scan_id"] for r in found.json()["reports"]] == [SCAN]
    other_company = client.get(f"/reports/access/history?company_id={OTHER}", headers=auth_header_factory(t))
    assert other_company.status_code == 200
    assert other_company.json()["reports"] == []
    other_tenant = tenant_factory()
    no_leak = client.get(f"/reports/access/history?company_id={COMPANY}", headers=auth_header_factory(other_tenant))
    assert no_leak.status_code == 200 and no_leak.json()["reports"] == []
    unauth = client.get(f"/reports/access/history?company_id={COMPANY}")
    assert unauth.status_code in (401, 403)


def test_bad_or_expired_access_code_never_grants_token(client, tenant_factory, scan_factory):
    t = _seed(tenant_factory, scan_factory)
    code = "a" * 45
    with SessionLocal() as db:
        db.add(ReportAccessGrant(
            token_hash=hashlib.sha256(code.encode()).hexdigest(),
            tenant_id=t["tenant_id"], company_id=COMPANY, scan_id=SCAN, variant="full",
            created_at_utc=datetime.now(timezone.utc) - timedelta(minutes=2),
            expires_at_utc=datetime.now(timezone.utc) - timedelta(minutes=1),
        ))
        db.commit()
    req = {"code": code, "scan_id": SCAN, "company_id": COMPANY, "report_variant": "full"}
    assert client.post("/reports/access/exchange", json=req).status_code == 403
    req["code"] = "not_a_valid_link"
    assert client.post("/reports/access/exchange", json=req).status_code == 422


def test_context_mismatch_consumes_code_without_leaking_report(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory, product_access_factory,
):
    t = _seed(tenant_factory, scan_factory)
    product_access_factory(tenant_id=t["tenant_id"])
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    from urllib.parse import urlparse, parse_qs
    link = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t)).json()["url"]
    code = parse_qs(urlparse(link).query)["code"][0]
    bad = {"code": code, "scan_id": SCAN, "company_id": OTHER, "report_variant": "full"}
    assert client.post("/reports/access/exchange", json=bad).status_code == 403
    bad["company_id"] = COMPANY
    assert client.post("/reports/access/exchange", json=bad).status_code == 403


def test_v2_full_archive_history_is_locked_after_premium_expiry(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory,
):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant = _seed(tenant_factory, scan_factory)
    headers = auth_header_factory(tenant)
    url = f"/reports/access/history?company_id={COMPANY}"
    expired = client.get(url, headers=headers)
    assert expired.status_code == 403
    _activate_full(tenant["tenant_id"])
    active = client.get(url, headers=headers)
    assert active.status_code == 200, active.text
    assert any(row["scan_id"] == SCAN for row in active.json()["reports"])
