"""Real stored-scan regression for DEV legacy-to-v6 Full projection.

Old staging executive reports intentionally carry only top-N findings. The Full
renderer must instead receive every stored issue, explicit deterministic
priority codes and a scan-bound validation baseline.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.db import SessionLocal
from app.models import Scan, Tenant, TenantScanCredit
from app.schemas.report import ExecutiveReport
from app.services import executive_report_v2_service as full
from app.services.product_license_service import PRODUCT_VALIDATION_CHECK


def _legacy_report(tenant_id: str, scan_id: str) -> ExecutiveReport:
    now = datetime.now(timezone.utc)
    return ExecutiveReport(
        report_id="exec-" + scan_id,
        tenant_id=tenant_id, language="de", scan_id=scan_id,
        scan_generated_at_utc=now, generated_at_utc=now,
        company_label="Beispiel GmbH", environment_label="Sandbox",
        executive_summary="Stored scan", data_health_score=80,
        score_status="Stabil", total_records=100, checks_count=5,
        issues_count=1, affected_records=1,
        headline="Finding", rating="ok",
    )


def test_legacy_staging_builder_enrichment_reads_every_stored_finding(
    tenant_factory, scan_factory, monkeypatch,
):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="legacy_to_full")
    monkeypatch.setattr(
        full, "resolve_check_texts",
        lambda db, codes, lang: {
            code: SimpleNamespace(title="Catalog title " + code, recommendation="Fix " + code)
            for code in codes
        },
    )
    with SessionLocal() as db:
        saved = db.get(Tenant, tenant["tenant_id"])
        result = full._enrich_staging_report(db, saved, _legacy_report(saved.tenant_id, "legacy_to_full"))
        assert [x.code for x in result.all_findings] == ["ISSUE_1"]
        assert result.all_findings[0].title == "Catalog title ISSUE_1"
        assert result.issues_count == len(result.all_findings)
        assert result.validation_baseline_scan_id == "legacy_to_full"
        assert result.validation_baseline_eligible is True
        assert {code for group in result.priority_matrix for code in group.finding_codes} == {"ISSUE_1"}
        assert sum(area.issue_count for area in result.business_area_impact) == 1


def test_validation_scan_is_not_mislabeled_full_baseline(
    tenant_factory, scan_factory, monkeypatch,
):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="validation_as_full")
    monkeypatch.setattr(
        full, "resolve_check_texts",
        lambda db, codes, lang: {
            code: SimpleNamespace(title=code, recommendation="Fix") for code in codes
        },
    )
    with SessionLocal() as db:
        db.add(TenantScanCredit(
            tenant_id=tenant["tenant_id"],
            product_code=PRODUCT_VALIDATION_CHECK,
            status="consumed",
            source="test_fixture",
            consumed_scan_id="validation_as_full",
            created_at_utc=datetime.now(timezone.utc),
        ))
        db.commit()
        saved = db.get(Tenant, tenant["tenant_id"])
        result = full._enrich_staging_report(db, saved, _legacy_report(saved.tenant_id, "validation_as_full"))
        assert result.validation_baseline_eligible is False
        assert result.validation_baseline_scan_id == "validation_as_full"
