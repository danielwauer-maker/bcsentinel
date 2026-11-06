"""Integration regression for BC-native Full report access and history.

No OIDC, BC API token stays server-side. All browser tokens are scoped to one
tenant/company/scan and all exchange codes are one-time.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from app.core.settings import settings
from app.db import SessionLocal
from app.models import Scan
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


def test_archived_report_can_be_launched_after_entitlement_ends_and_code_is_one_use(
    client, monkeypatch, tenant_factory, scan_factory, auth_header_factory
):
    t = _seed(tenant_factory, scan_factory)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
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


def test_context_mismatch_consumes_code_without_leaking_report(client, monkeypatch, tenant_factory, scan_factory, auth_header_factory):
    t = _seed(tenant_factory, scan_factory)
    monkeypatch.setattr(settings, "REPORT_V6_VIEWER_BASE_URL", "https://reports.example.test")
    from urllib.parse import urlparse, parse_qs
    link = client.post(f"/reports/executive/{SCAN}/v6-link", headers=auth_header_factory(t)).json()["url"]
    code = parse_qs(urlparse(link).query)["code"][0]
    bad = {"code": code, "scan_id": SCAN, "company_id": OTHER, "report_variant": "full"}
    assert client.post("/reports/access/exchange", json=bad).status_code == 403
    bad["company_id"] = COMPANY
    assert client.post("/reports/access/exchange", json=bad).status_code == 403
