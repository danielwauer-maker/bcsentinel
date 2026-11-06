from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace as NS
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services import full_report_render_service as svc


NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)
COMPANY = "11111111-2222-3333-4444-555555555555"


class FakeDb:
    def __init__(self, captured=None, rows=None):
        self.captured = captured
        self.rows = [] if rows is None else rows

    def get(self, _table, _id):
        return self.captured

    def scalars(self, _query):
        return NS(all=lambda: self.rows)


def fixtures(n: int = 27, *, impact_mismatch=False, confirmed=True):
    tenant = NS(tenant_id="company_test_tenant")
    scan = NS(scan_id="scan_verified_full", tenant_id=tenant.tenant_id,
              bc_company_id=COMPANY, lcy_code="EUR")
    scope = NS(tenant_id=tenant.tenant_id, state="confirmed" if confirmed else "auto",
               confirmed_at_utc=NOW if confirmed else None, included_modules_count=10,
               score_value=72, version=3)
    severity_cycle = ["critical", "high", "medium", "low", "info"]
    findings = [
        NS(rank=i + 1, code=f"F-{i:03}", title=f"Real finding {i}", category="Finance",
           severity=severity_cycle[i % len(severity_cycle)], affected_count=i * 3 + 1,
           estimated_impact_eur=100.0, recommendation=f"Action for {i}")
        for i in range(n)
    ]
    groups = []
    for p, selected in [
        ("P1", [f for f in findings if f.severity == "critical"]),
        ("P2", [f for f in findings if f.severity == "high"]),
        ("P3", [f for f in findings if f.severity not in ("critical", "high")]),
    ]:
        if selected:
            groups.append(NS(priority=p, focus=p + " findings",
                             recommendation="Review evidence", finding_codes=[f.code for f in selected]))
    sum_impact = float(n * 100 + (7 if impact_mismatch else 0))
    report = NS(
        validation_baseline_eligible=True, validation_baseline_scan_id=scan.scan_id,
        data_health_score=72, scan_generated_at_utc=NOW,
        company_label="Customer Ltd", environment_label="PROD",
        all_findings=findings, issues_count=n, priority_matrix=groups,
        business_area_impact=[NS(name="Finance", score=72, estimated_impact_eur=sum_impact)],
        estimated_loss_eur=sum_impact, potential_saving_eur=30.0,
        language="en", total_records=1000, checks_count=45,
        executive_summary="Customer-owned actual scan evidence, not illustrative.",
        headline="Data quality needs improvement",
    )
    return tenant, scan, scope, report


@pytest.mark.parametrize("count", [0, 1, 27, 55, 90])
def test_full_projection_never_fabricates_findings(monkeypatch, count):
    tenant, scan, scope, report = fixtures(count)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda _db, _sid: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda _db, _tenant, _sid: report)
    result = svc.build_full_render_vm(FakeDb(), tenant, scan)
    assert result["basis"] == "scan_evidence"
    assert result["meta"]["company"] == "Customer Ltd"
    assert result["scope"]["findingCount"] == count
    assert result["detailCoverage"] == {"total": count, "detailed": count}
    assert sum(result["severity"].values()) == count
    assert len(result["featuredFindings"]) == min(3, count)
    assert len(result["topFindings"]) == min(10, count)
    assert len(result["appendix"]) == max(0, count - 10)
    assert {f["code"] for f in result["appendix"]}.isdisjoint({f["code"] for f in result["topFindings"]})
    assert result["exceptions"]["status"] == "not_supplied"
    assert all(f["observation"] is None and f["relevance"] is None for f in result["topFindings"])


def test_confirmed_scope_is_mandatory(monkeypatch):
    tenant, scan, scope, report = fixtures(10, confirmed=False)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    with pytest.raises(HTTPException) as exc:
        svc.build_full_render_vm(FakeDb(), tenant, scan)
    assert exc.value.status_code == 409


def test_failed_financial_reconciliation_is_disclosed(monkeypatch):
    tenant, scan, scope, report = fixtures(10, impact_mismatch=True)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    view = svc.build_full_render_vm(FakeDb(), tenant, scan)
    assert view["impactModel"]["reconciliationStatus"] == "backend_unreconciled"
    assert view["totalImpactEur"] == 1007
    assert view["detailCoverage"]["total"] == 10


def test_known_empty_exception_capture_is_not_unknown(monkeypatch):
    tenant, scan, scope, report = fixtures(2)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    capture = NS(tenant_id=tenant.tenant_id, exception_count=0)
    view = svc.build_full_render_vm(FakeDb(captured=capture), tenant, scan)
    assert view["exceptions"] == {"status": "confirmed_none", "scopeVersion": "v3"}


def test_unexpected_exception_count_blocks(monkeypatch):
    tenant, scan, scope, report = fixtures(2)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    capture = NS(tenant_id=tenant.tenant_id, exception_count=2)
    with pytest.raises(HTTPException) as exc:
        svc.build_full_render_vm(FakeDb(captured=capture), tenant, scan)
    assert exc.value.status_code == 409


def test_out_of_scope_or_duplicated_priority_blocks(monkeypatch):
    tenant, scan, scope, report = fixtures(4)
    report.priority_matrix[0].finding_codes.append("not-verified")
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    with pytest.raises(HTTPException):
        svc.build_full_render_vm(FakeDb(), tenant, scan)


def test_invalid_or_missing_eur_currency_blocks(monkeypatch):
    tenant, scan, scope, report = fixtures(4)
    scan.lcy_code = "SEK"
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    with pytest.raises(HTTPException) as exc:
        svc.build_full_render_vm(FakeDb(), tenant, scan)
    assert exc.value.status_code == 409


def test_captured_exceptions_without_verified_classification_fail_closed(monkeypatch):
    """An exception reason alone does not prove accepted_risk, N/A or status."""
    tenant, scan, scope, report = fixtures(2)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    capture = NS(tenant_id=tenant.tenant_id, exception_count=1)
    captured = NS(company_id=COMPANY, issue_code="F-000", reason="Business note")
    with pytest.raises(HTTPException) as exc:
        svc.build_full_render_vm(FakeDb(captured=capture, rows=[captured]), tenant, scan)
    assert exc.value.status_code == 409
    assert "no verified type/status evidence" in str(exc.value.detail)


def test_captured_exception_from_other_company_fails_closed(monkeypatch):
    tenant, scan, scope, report = fixtures(2)
    monkeypatch.setattr(svc, "get_latest_confirmed_scope", lambda *_: scope)
    monkeypatch.setattr(svc, "build_executive_report", lambda *_: report)
    capture = NS(tenant_id=tenant.tenant_id, exception_count=1)
    captured = NS(company_id="99999999-2222-3333-4444-555555555555", issue_code="F-000", reason="Note")
    with pytest.raises(HTTPException) as exc:
        svc.build_full_render_vm(FakeDb(captured=capture, rows=[captured]), tenant, scan)
    assert exc.value.status_code == 409
    assert "another BC company" in str(exc.value.detail)
