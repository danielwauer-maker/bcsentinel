"""Live Full Assessment v6 projection from authenticated scan evidence only.

This module never reads the Contoso seed or invents observations, root causes,
customer-reconciled financial figures, or unrecorded scope exceptions.
"""
from __future__ import annotations

from collections import Counter
from datetime import timezone
from math import isclose

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment_scope_models import AssessmentScopeSnapshot
from app.exception_snapshot_models import ScanExceptionSnapshot, ScanExceptionSnapshotCapture
from app.models import Scan, Tenant
from app.schemas.report import ExecutiveReport
from app.services.assessment_scope_service import get_latest_confirmed_scope
from app.services.executive_report_v2_service import build_executive_report

SEVERITIES = ("critical", "high", "medium", "low", "info")
AREA_KEYS = {
    "Finance": "Finanzen", "Sales": "Verkauf",
    "Purchasing": "Einkauf", "Inventory": "Lager & Artikel",
    "CRM": "CRM & Stammdaten", "Manufacturing": "Produktion",
    "Service": "Service", "Jobs": "Projekte", "HR": "Personal",
    "System": "System & Plattform",
}


def _deny(reason: str) -> None:
    raise HTTPException(status_code=409, detail=f"Full report evidence unavailable: {reason}")


def _severity(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in SEVERITIES:
        _deny("unrecognized finding severity")
    return normalized


def _currency(value: float) -> float:
    result = round(float(value), 2)
    if result < 0:
        _deny("negative modeled impact")
    return result


def build_full_render_vm(db: Session, tenant: Tenant, scan: Scan) -> dict:
    """Build a v6 view model ONLY for a confirmed, complete, EUR-source snapshot.

    The caller checks user membership, tenant, BC-company, LCY, and paid Full
    entitlement independently. This service verifies all available evidence.
    """
    scope = get_latest_confirmed_scope(db, scan.scan_id)
    if (
        scope is None or scope.tenant_id != tenant.tenant_id
        or scope.state != "confirmed" or scope.confirmed_at_utc is None
        or scope.included_modules_count < 1
    ):
        _deny("confirmed scope snapshot missing")
    if str(scan.lcy_code or "").upper() != "EUR":
        _deny("verified EUR financial report currency unavailable")

    report: ExecutiveReport = build_executive_report(db, tenant, scan.scan_id)
    if report.validation_baseline_eligible is not True:
        _deny("scan is not a Full Assessment baseline")
    if report.validation_baseline_scan_id != scan.scan_id:
        _deny("baseline scan mismatch")
    if report.data_health_score != scope.score_value:
        _deny("confirmed score mismatch")
    if not report.scan_generated_at_utc:
        _deny("scan time missing")
    if not report.company_label.strip():
        _deny("company label missing")

    findings = list(report.all_findings)
    codes = [f.code for f in findings]
    if not all(code and str(code).strip() for code in codes) or len(codes) != len(set(codes)):
        _deny("missing or repeated finding IDs")
    if report.issues_count != len(findings):
        _deny("finding count does not match scoped findings")

    severity = {s: 0 for s in SEVERITIES}
    for f in findings:
        severity[_severity(f.severity)] += 1
        if f.category not in AREA_KEYS:
            _deny("unsupported or unmapped business area")

    # Business priority must originate from the report's own priority groups;
    # apply first matching group in P1>P2>P3 order if a legacy overlap exists,
    # never arbitrarily assign a priority to a missing ID.
    priorities = {}
    groups = sorted(report.priority_matrix, key=lambda x: {"P1": 0, "P2": 1, "P3": 2}.get(x.priority, 99))
    for group in groups:
        if group.priority not in ("P1", "P2", "P3"):
            _deny("unrecognized priority group")
        for code in group.finding_codes:
            if code not in codes:
                _deny("priority refers to a finding outside confirmed scope")
            priorities.setdefault(code, group.priority)
    if len(priorities) != len(findings):
        _deny("not all findings have verified priority assignment")

    priority_counts = Counter(priorities.values())
    priorities_vm = []
    for group in groups:
        n = priority_counts.get(group.priority, 0)
        if n:
            priorities_vm.append({
                "priority": group.priority, "title": group.focus,
                "findings": n, "text": group.recommendation,
            })

    area_rows = []
    for row in report.business_area_impact:
        if row.name not in AREA_KEYS:
            _deny("unmapped business area impact")
        area_rows.append({
            "area": AREA_KEYS[row.name],
            "score": row.score, "impactEur": _currency(row.estimated_impact_eur),
        })
    # Include every customer-confirmed supported standard area, including
    # those with zero detected findings. The score comes from the immutable
    # scope module snapshot, never from a fabricated demo area score.
    module_areas = {
        "system": "System & Plattform", "finance": "Finanzen",
        "sales": "Verkauf", "purchasing": "Einkauf",
        "inventory": "Lager & Artikel", "crm": "CRM & Stammdaten",
        "manufacturing": "Produktion", "service": "Service",
        "jobs": "Projekte", "hr": "Personal",
    }
    existing_area_names = {row["area"] for row in area_rows}
    for module in getattr(scope, "modules", []):
        if not module.included_in_score:
            continue
        area_name = module_areas.get(module.module_code)
        if not area_name:
            _deny("confirmed scope contains unsupported business area")
        if area_name not in existing_area_names:
            area_rows.append({
                "area": area_name,
                "score": module.module_score,
                "impactEur": 0.0,
            })
            existing_area_names.add(area_name)
    finding_impact = round(sum(_currency(f.estimated_impact_eur) for f in findings), 2)
    area_impact = round(sum(row["impactEur"] for row in area_rows), 2)
    total_impact = _currency(report.estimated_loss_eur)
    reconciled = isclose(finding_impact, area_impact, abs_tol=0.01) and isclose(
        area_impact, total_impact, abs_tol=0.01
    )
    # A mismatch remains visible as *unreconciled*, not as a false savings claim.
    language = "de" if str(report.language).lower().startswith("de") else "en"
    note = (
        "Modellierter Einzel- und Bereichs-Impact ist nicht vollständig abgestimmt; Werte nicht addieren."
        if language == "de" else
        "Modeled finding exposure and business-area impact are not fully reconciled; do not add the values."
    ) if not reconciled else (
        "Modellwerte stimmen rechnerisch überein; keine nachgewiesenen Einsparungen."
        if language == "de" else
        "Modeled values reconcile arithmetically; they are not realized savings."
    )

    detail = []
    for f in findings:
        detail.append({
            "rank": f.rank, "code": f.code, "title": f.title,
            "canonicalArea": None, "area": AREA_KEYS[f.category],
            "severity": _severity(f.severity),
            "affectedRecords": f.affected_count,
            "impactEur": _currency(f.estimated_impact_eur),
            "observation": None, "relevance": None,
            "recommendation": f.recommendation or None,
            "priority": priorities[f.code],
        })
    detail.sort(key=lambda x: (x["rank"], x["code"]))

    capture = db.get(ScanExceptionSnapshotCapture, scan.scan_id)
    captured = db.scalars(
        select(ScanExceptionSnapshot).where(
            ScanExceptionSnapshot.scan_id == scan.scan_id,
            ScanExceptionSnapshot.tenant_id == tenant.tenant_id,
        ).order_by(ScanExceptionSnapshot.source_exception_entry_no)
    ).all()
    snapshot_version = f"v{scope.version}"
    if capture is None:
        exceptions: dict = {"status": "not_supplied", "scopeVersion": snapshot_version}
    elif capture.tenant_id != tenant.tenant_id or capture.exception_count != len(captured):
        _deny("exception snapshot count or tenant mismatch")
    elif not captured:
        exceptions = {"status": "confirmed_none", "scopeVersion": snapshot_version}
    else:
        # The current immutable snapshot records an issue code and reason, but no
        # verified exception classification (accepted risk / N/A / unsupported)
        # or status. Do not invent accepted_risk or a lifecycle status for live
        # customer reports. Until BC captures these typed fields, fail closed.
        for item in captured:
            if item.company_id and item.company_id.lower() != scan.bc_company_id.lower():
                _deny("exception from another BC company")
        _deny("captured exceptions have no verified type/status evidence")

    timestamp = report.scan_generated_at_utc.astimezone(timezone.utc).isoformat()
    top = detail[:10]
    featured = detail[:3]
    featured_codes = {f["code"] for f in featured}
    top_codes = {f["code"] for f in top}
    # Non-top findings are included once in the appendix, including 50+ rows.
    appendix = [f for f in detail if f["code"] not in top_codes and f["code"] not in featured_codes]
    return {
        "basis": "scan_evidence", "kind": "full",
        "meta": {
            "company": report.company_label,
            "environment": report.environment_label,
            "scanDateTime": timestamp, "scanId": scan.scan_id,
        },
        "score": {
            "kind": "confirmed_baseline", "value": report.data_health_score,
            "baselineConfirmed": True,
        },
        "scope": {
            "status": "confirmed_supported",
            "analyzedRecords": report.total_records,
            "checksRun": report.checks_count,
            "areasAnalyzed": scope.included_modules_count,
            "findingCount": len(findings),
        },
        "severity": severity,
        "businessAreas": area_rows,
        "totalImpactEur": total_impact,
        "improvementPotentialEur": _currency(report.potential_saving_eur),
        "impactModel": {
            "findingValueType": "modeledFindingExposure",
            "areaValueType": "modeledBusinessAreaImpact",
            "reconciliationStatus": "backend_reconciled" if reconciled else "backend_unreconciled",
            "note": note,
        },
        "detailCoverage": {"total": len(findings), "detailed": len(detail)},
        "summary": report.executive_summary,
        "conclusion": report.headline or report.executive_summary,
        "topFindings": top, "featuredFindings": featured,
        "priorities": priorities_vm,
        "validationBaseline": {
            "score": report.data_health_score,
            "findings": len(findings),
            "critical": severity["critical"], "high": severity["high"],
            "impactEur": total_impact,
            "potentialEur": _currency(report.potential_saving_eur),
        },
        # These must not be misrepresented as benefits: no scan-specific
        # evidence model currently proves the benefits; retain empty list.
        "improvementBenefits": [],
        "appendix": appendix,
        "exceptions": exceptions,
    }
