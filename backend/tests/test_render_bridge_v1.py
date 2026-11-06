from __future__ import annotations

from app.db import SessionLocal
from app.models import Scan
from app.routers import report_render_data as bridge

COMPANY_A = "11111111-2222-3333-4444-555555555555"
COMPANY_B = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _setup(monkeypatch, tenant_factory, scan_factory, *, currency="EUR", bound=True):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_bridge_1")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_bridge_1").one()
        scan.bc_company_id = COMPANY_A if bound else None
        scan.lcy_code = currency if bound else None
        db.commit()
    monkeypatch.setattr(
        bridge, "_tenant_user_principal",
        lambda _authorization: (123, tenant["tenant_id"], "VIEWER"),
    )
    return tenant


def test_tenant_user_session_required(client):
    res = client.get(f"/account/reports/free/unknown?company_id={COMPANY_A}")
    assert res.status_code in (401, 403)


def test_free_company_bound_response_is_aggregate_only(client, monkeypatch, tenant_factory, scan_factory):
    tenant = _setup(monkeypatch, tenant_factory, scan_factory)
    res = client.get(f"/account/reports/free/scan_bridge_1?company_id={COMPANY_A}")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["contract_version"] == "bcsentinel-render-bridge-v1"
    assert data["tenant_id"] == tenant["tenant_id"]
    assert data["company_id"] == COMPANY_A
    assert data["source"] == "live"
    assert data["variant"] == "free"
    assert data["currency"]["company_lcy_code"] == "EUR"
    assert res.headers["cache-control"].startswith("no-store")
    assert "all_findings" not in data["report"]
    assert "top_findings" not in data["report"]
    assert "estimated_loss_eur" not in data["report"]
    assert "potential_saving_eur" not in data["report"]


def test_different_company_is_indistinguishable_from_missing_scan(client, monkeypatch, tenant_factory, scan_factory):
    _setup(monkeypatch, tenant_factory, scan_factory)
    res = client.get(f"/account/reports/free/scan_bridge_1?company_id={COMPANY_B}")
    assert res.status_code == 404


def test_legacy_unbound_scan_fails_closed(client, monkeypatch, tenant_factory, scan_factory):
    _setup(monkeypatch, tenant_factory, scan_factory, bound=False)
    res = client.get(f"/account/reports/free/scan_bridge_1?company_id={COMPANY_A}")
    assert res.status_code == 409


def test_non_eur_financial_report_requires_verified_fx(client, monkeypatch, tenant_factory, scan_factory):
    _setup(monkeypatch, tenant_factory, scan_factory, currency="SEK")
    # The currency guard precedes every Full/Validation/Monitoring builder.
    for variant in ("full", "validation", "monitoring"):
        res = client.get(f"/account/reports/{variant}/scan_bridge_1?company_id={COMPANY_A}")
        assert res.status_code == 409
        assert "conversion" in res.json()["detail"].lower()


def test_quick_entitlement_is_enforced_before_details(client, monkeypatch, tenant_factory, scan_factory):
    _setup(monkeypatch, tenant_factory, scan_factory)
    monkeypatch.setattr(bridge, "build_quick_assessment_access_snapshot", lambda db, tenant: {"can_view_quick_assessment": False})
    res = client.get(f"/account/reports/quick/scan_bridge_1?company_id={COMPANY_A}")
    assert res.status_code == 402


def test_full_entitlement_is_enforced_before_details(client, monkeypatch, tenant_factory, scan_factory):
    _setup(monkeypatch, tenant_factory, scan_factory)
    monkeypatch.setattr(bridge, "build_product_access_snapshot", lambda db, tenant: {"can_view_executive_report": False})
    res = client.get(f"/account/reports/full/scan_bridge_1?company_id={COMPANY_A}")
    assert res.status_code == 402
