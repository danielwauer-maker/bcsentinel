"""Real ORM contract: the confirmed Full scope excludes extension findings."""
from __future__ import annotations

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, ScanRunStatus, Tenant
from app.services.assessment_scope_service import confirm_scope
from app.services.full_report_render_service import build_full_render_vm

COMPANY = "11111111-2222-3333-4444-555555555555"


def test_confirmed_standard_scope_excludes_custom_extension_and_unknown_areas(
    tenant_factory, scan_factory,
):
    tenant_info = tenant_factory()
    scan_factory(tenant_id=tenant_info["tenant_id"], scan_id="full_standard_only")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "full_standard_only").one()
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_info["tenant_id"]).one()
        scan.bc_company_id = COMPANY
        scan.lcy_code = "EUR"
        # Full v6 intentionally requires an evidence-backed BC company label.
        # Provide real scan-run provenance in this integration fixture rather
        # than weakening the fail-closed production renderer.
        db.add(ScanRunStatus(
            run_id=scan.scan_id,
            tenant_id=tenant.tenant_id,
            company_name="Test BC Company",
            environment_name="Sandbox",
            status="completed",
            updated_at_utc=scan.generated_at_utc,
        ))
        scan.estimated_loss_eur = 55.0
        scan.potential_saving_eur = 10.0
        # The scan_factory existing legacy ISSUE_1 has no category and is
        # unsupported until the original BC module/category is known.
        db.add(ScanIssueRecord(
            scan_id=scan.scan_id, code="FIN_SUPPORTED", category="Finance",
            title="Verified GL issue", severity="critical", affected_count=2,
            premium_only=False, recommendation_preview="Check posting setup",
            estimated_impact_eur=10.0,
        ))
        db.add(ScanIssueRecord(
            scan_id=scan.scan_id, code="CUSTOM_EXTENSION", category="Custom Finance Workflow",
            title="Custom extension rule", severity="high", affected_count=4,
            premium_only=True, recommendation_preview="Extension-specific",
            estimated_impact_eur=45.0,
        ))
        db.commit()
        confirmed = confirm_scope(db, scan, {})
        assert confirmed.state == "confirmed"
        vm = build_full_render_vm(db, tenant, scan)

    assert vm["score"]["value"] == confirmed.score_value
    assert vm["scope"]["findingCount"] == 1
    assert vm["detailCoverage"] == {"total": 1, "detailed": 1}
    assert [row["code"] for row in vm["topFindings"]] == ["FIN_SUPPORTED"]
    assert vm["totalImpactEur"] == 10.0
    assert sum(area["impactEur"] for area in vm["businessAreas"]) == 10.0
    assert vm["impactModel"]["reconciliationStatus"] == "backend_reconciled"
