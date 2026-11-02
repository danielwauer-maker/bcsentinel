from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, Tenant, TenantScanCredit
from app.operator_models import TenantOperatorAction
from app.schemas.validation_report import (
    ValidationBusinessAreaDelta,
    ValidationFindingDelta,
    ValidationReport,
)
from app.services.localization_service import tenant_language
from app.services.product_license_service import PRODUCT_VALIDATION_CHECK
from app.services.quick_finding_selection_service import normalize_severity

SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
BUSINESS_AREAS = (
    "Finance",
    "Sales",
    "Purchasing",
    "Inventory",
    "CRM",
    "Manufacturing",
    "Service",
    "Jobs",
    "HR",
    "System",
)
BUSINESS_AREA_SCORE_ATTRS = {
    "Finance": "finance_score",
    "Sales": "sales_score",
    "Purchasing": "purchasing_score",
    "Inventory": "inventory_score",
    "CRM": "crm_score",
    "Manufacturing": "manufacturing_score",
    "Service": "service_score",
    "Jobs": "jobs_score",
    "HR": "hr_score",
    "System": "system_score",
}
BUSINESS_AREA_LABELS_DE = {
    "Finance": "Finanzen",
    "Sales": "Verkauf",
    "Purchasing": "Einkauf",
    "Inventory": "Lager & Artikel",
    "CRM": "CRM & Stammdaten",
    "Manufacturing": "Produktion",
    "Service": "Service",
    "Jobs": "Projekte",
    "HR": "Personal",
    "System": "System",
}


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: object) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _bounded_score(value: object) -> int:
    return max(0, min(100, _safe_int(value)))


def _normalize_category(value: str | None, code: str | None = None) -> str:
    raw = str(value or "").strip().lower()
    code_upper = str(code or "").upper()
    mapping = {
        "finance": "Finance",
        "sales": "Sales",
        "sale": "Sales",
        "purchase": "Purchasing",
        "purchasing": "Purchasing",
        "inventory": "Inventory",
        "item": "Inventory",
        "crm": "CRM",
        "customer": "CRM",
        "vendor": "Purchasing",
        "manufacturing": "Manufacturing",
        "service": "Service",
        "jobs": "Jobs",
        "job": "Jobs",
        "hr": "HR",
        "system": "System",
    }
    if raw in mapping:
        return mapping[raw]
    if code_upper.startswith(("CUSTOMER", "CUSTOMERS")):
        return "CRM"
    if code_upper.startswith(("VENDOR", "VENDORS", "PURCHASE", "PURCH")):
        return "Purchasing"
    if code_upper.startswith(("ITEM", "ITEMS", "INVENTORY", "WAREHOUSE", "VALUE")):
        return "Inventory"
    if code_upper.startswith(("SALE", "SALES")):
        return "Sales"
    if "LEDGER" in code_upper or code_upper.startswith(("GL_", "G_L_")):
        return "Finance"
    return "System"


def _business_area_label(category: str, language: str) -> str:
    if language == "de":
        return BUSINESS_AREA_LABELS_DE.get(category, BUSINESS_AREA_LABELS_DE["System"])
    return category if category in BUSINESS_AREAS else "System"


def _load_validation_credit(db: Session, tenant: Tenant, validation_scan_id: str) -> TenantScanCredit:
    credit = db.scalar(
        select(TenantScanCredit).where(
            TenantScanCredit.tenant_id == tenant.tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == validation_scan_id,
        )
    )
    if credit is None:
        raise HTTPException(status_code=404, detail="Scan is not a completed BCSentinel Validation scan.")
    return credit


def _load_validation_scan(db: Session, tenant: Tenant, validation_scan_id: str) -> tuple[Scan, TenantScanCredit]:
    scan = db.scalar(
        select(Scan).where(
            Scan.scan_id == validation_scan_id,
            Scan.tenant_id == tenant.tenant_id,
        )
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Validation report not found.")
    return scan, _load_validation_credit(db, tenant, validation_scan_id)


def _is_validation_scan(db: Session, tenant_id: str, scan_id: str) -> bool:
    return db.scalar(
        select(TenantScanCredit.id).where(
            TenantScanCredit.tenant_id == tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == scan_id,
        )
    ) is not None


def _validate_baseline_scan(db: Session, tenant: Tenant, validation_scan: Scan, baseline_scan_id: str) -> Scan:
    baseline = db.scalar(
        select(Scan).where(
            Scan.tenant_id == tenant.tenant_id,
            Scan.scan_id == baseline_scan_id,
        )
    )
    if baseline is None:
        raise HTTPException(status_code=409, detail="The Validation baseline scan no longer exists.")
    is_prior = (
        baseline.generated_at_utc < validation_scan.generated_at_utc
        or (
            baseline.generated_at_utc == validation_scan.generated_at_utc
            and baseline.id < validation_scan.id
        )
    )
    if not is_prior:
        raise HTTPException(status_code=409, detail="Validation baseline must predate the Validation scan.")
    if _is_validation_scan(db, tenant.tenant_id, baseline.scan_id):
        raise HTTPException(status_code=409, detail="A Validation scan cannot be used as the Full Assessment baseline.")
    return baseline


def _legacy_baseline_scan(db: Session, tenant: Tenant, validation_scan: Scan) -> Scan:
    candidates = db.scalars(
        select(Scan)
        .where(
            Scan.tenant_id == tenant.tenant_id,
            Scan.scan_id != validation_scan.scan_id,
            or_(
                Scan.generated_at_utc < validation_scan.generated_at_utc,
                and_(
                    Scan.generated_at_utc == validation_scan.generated_at_utc,
                    Scan.id < validation_scan.id,
                ),
            ),
        )
        .order_by(Scan.generated_at_utc.desc(), Scan.id.desc())
    ).all()
    baseline = next(
        (scan for scan in candidates if not _is_validation_scan(db, tenant.tenant_id, scan.scan_id)),
        None,
    )
    if baseline is None:
        raise HTTPException(status_code=409, detail="Validation requires an earlier Full Assessment baseline scan.")
    return baseline


def _load_baseline_scan(
    db: Session,
    tenant: Tenant,
    validation_scan: Scan,
    validation_credit: TenantScanCredit,
) -> tuple[Scan, str]:
    # VR4 baseline precedence:
    # 1) explicit immutable baseline stored on the Validation scan credit,
    # 2) operator grant audit that already stores the exact Assessment scan,
    # 3) legacy compatibility fallback for older/direct records only.
    if validation_credit.baseline_scan_id:
        return (
            _validate_baseline_scan(db, tenant, validation_scan, validation_credit.baseline_scan_id),
            "validation_credit",
        )

    action = db.scalar(
        select(TenantOperatorAction)
        .where(
            TenantOperatorAction.tenant_id == tenant.tenant_id,
            TenantOperatorAction.action_type == "validation_grant",
            TenantOperatorAction.status == "completed",
            TenantOperatorAction.credit_id == validation_credit.id,
            TenantOperatorAction.related_scan_id.is_not(None),
        )
        .order_by(TenantOperatorAction.created_at_utc.desc(), TenantOperatorAction.id.desc())
        .limit(1)
    )
    if action is not None and action.related_scan_id:
        return (
            _validate_baseline_scan(db, tenant, validation_scan, action.related_scan_id),
            "operator_validation_grant",
        )

    return _legacy_baseline_scan(db, tenant, validation_scan), "legacy_prior_assessment"


def _issue_map(db: Session, scan_id: str) -> dict[str, ScanIssueRecord]:
    rows = db.scalars(
        select(ScanIssueRecord)
        .where(ScanIssueRecord.scan_id == scan_id)
        .order_by(ScanIssueRecord.code.asc())
    ).all()
    return {row.code: row for row in rows}


def _status(before: ScanIssueRecord | None, after: ScanIssueRecord | None) -> str:
    if before is None:
        return "new"
    if after is None:
        return "resolved"

    before_severity = SEVERITY_RANK[normalize_severity(before.severity)]
    after_severity = SEVERITY_RANK[normalize_severity(after.severity)]
    before_affected = _safe_int(before.affected_count)
    after_affected = _safe_int(after.affected_count)
    before_impact = _safe_float(before.estimated_impact_eur)
    after_impact = _safe_float(after.estimated_impact_eur)

    if after_severity > before_severity or after_affected > before_affected or after_impact > before_impact + 0.01:
        return "regressed"
    if after_severity < before_severity or after_affected < before_affected or after_impact < before_impact - 0.01:
        return "improved"
    return "remaining"


def _delta(
    before: ScanIssueRecord | None,
    after: ScanIssueRecord | None,
    status: str,
    language: str,
) -> ValidationFindingDelta:
    source = after or before
    assert source is not None
    category = _normalize_category(source.category, source.code)
    return ValidationFindingDelta(
        code=source.code,
        title=source.title,
        category=category,
        category_label=_business_area_label(category, language),
        severity_before=normalize_severity(before.severity) if before else None,
        severity_after=normalize_severity(after.severity) if after else None,
        affected_before=max(0, _safe_int(before.affected_count)) if before else 0,
        affected_after=max(0, _safe_int(after.affected_count)) if after else 0,
        impact_before_eur=round(max(0.0, _safe_float(before.estimated_impact_eur)), 2) if before else 0.0,
        impact_after_eur=round(max(0.0, _safe_float(after.estimated_impact_eur)), 2) if after else 0.0,
        status=status,
    )


def _aggregate_issue_metrics(rows: dict[str, ScanIssueRecord]) -> dict[str, dict[str, float | int]]:
    metrics: dict[str, dict[str, float | int]] = {
        area: {"findings": 0, "affected": 0, "impact": 0.0} for area in BUSINESS_AREAS
    }
    for issue in rows.values():
        area = _normalize_category(issue.category, issue.code)
        bucket = metrics[area]
        bucket["findings"] = int(bucket["findings"]) + 1
        bucket["affected"] = int(bucket["affected"]) + max(0, _safe_int(issue.affected_count))
        bucket["impact"] = float(bucket["impact"]) + max(0.0, _safe_float(issue.estimated_impact_eur))
    return metrics


def _business_area_deltas(
    baseline_scan: Scan,
    validation_scan: Scan,
    before_map: dict[str, ScanIssueRecord],
    after_map: dict[str, ScanIssueRecord],
    language: str,
) -> list[ValidationBusinessAreaDelta]:
    before_metrics = _aggregate_issue_metrics(before_map)
    after_metrics = _aggregate_issue_metrics(after_map)
    rows: list[ValidationBusinessAreaDelta] = []
    for area in BUSINESS_AREAS:
        score_attr = BUSINESS_AREA_SCORE_ATTRS[area]
        before_score = _bounded_score(getattr(baseline_scan, score_attr, 0))
        after_score = _bounded_score(getattr(validation_scan, score_attr, 0))
        before = before_metrics[area]
        after = after_metrics[area]
        before_findings = int(before["findings"])
        after_findings = int(after["findings"])
        before_affected = int(before["affected"])
        after_affected = int(after["affected"])
        before_impact = round(float(before["impact"]), 2)
        after_impact = round(float(after["impact"]), 2)
        rows.append(
            ValidationBusinessAreaDelta(
                name=area,
                label=_business_area_label(area, language),
                baseline_score=before_score,
                validation_score=after_score,
                score_delta=after_score - before_score,
                baseline_findings_count=before_findings,
                validation_findings_count=after_findings,
                findings_delta=after_findings - before_findings,
                baseline_affected_records=before_affected,
                validation_affected_records=after_affected,
                affected_records_delta=after_affected - before_affected,
                baseline_estimated_impact_eur=before_impact,
                validation_estimated_impact_eur=after_impact,
                estimated_impact_delta_eur=round(after_impact - before_impact, 2),
            )
        )
    return rows


def _affected_records(rows: dict[str, ScanIssueRecord]) -> int:
    return sum(max(0, _safe_int(issue.affected_count)) for issue in rows.values())


def build_validation_report(db: Session, tenant: Tenant, validation_scan_id: str) -> ValidationReport:
    language = tenant_language(tenant)
    validation_scan, validation_credit = _load_validation_scan(db, tenant, validation_scan_id)
    baseline_scan, baseline_reference_source = _load_baseline_scan(
        db,
        tenant,
        validation_scan,
        validation_credit,
    )

    before_map = _issue_map(db, baseline_scan.scan_id)
    after_map = _issue_map(db, validation_scan.scan_id)
    all_codes = sorted(set(before_map) | set(after_map))

    buckets: dict[str, list[ValidationFindingDelta]] = {
        "resolved": [],
        "improved": [],
        "remaining": [],
        "regressed": [],
        "new": [],
    }
    for code in all_codes:
        before = before_map.get(code)
        after = after_map.get(code)
        status = _status(before, after)
        buckets[status].append(_delta(before, after, status, language))

    business_areas = _business_area_deltas(baseline_scan, validation_scan, before_map, after_map, language)
    baseline_score = _bounded_score(baseline_scan.data_score)
    validation_score = _bounded_score(validation_scan.data_score)
    baseline_issues = max(0, _safe_int(baseline_scan.issues_count))
    validation_issues = max(0, _safe_int(validation_scan.issues_count))
    baseline_affected = _affected_records(before_map)
    validation_affected = _affected_records(after_map)
    baseline_loss = round(max(0.0, _safe_float(baseline_scan.estimated_loss_eur)), 2)
    validation_loss = round(max(0.0, _safe_float(validation_scan.estimated_loss_eur)), 2)
    score_delta = validation_score - baseline_score
    loss_delta = round(validation_loss - baseline_loss, 2)
    exposure_reduction = round(max(0.0, baseline_loss - validation_loss), 2)

    if language == "de":
        executive_summary = (
            f"Die Validierung vergleicht den neuen Deep Scan {validation_scan.scan_id} mit der Full-Assessment-Baseline "
            f"{baseline_scan.scan_id}. Der Data Health Score verändert sich um {score_delta:+d} Punkte auf "
            f"{validation_score}/100. {len(buckets['resolved'])} Findings wurden behoben, "
            f"{len(buckets['improved'])} verbessert und {len(buckets['new'])} neu erkannt."
        )
        next_steps = [
            "Neue oder verschlechterte Findings zuerst prüfen und priorisieren.",
            "Verbleibende High-Impact-Findings in der nächsten Bereinigungswelle schließen.",
            "Monitoring nutzen, wenn die Datenqualität nach der Validierung kontinuierlich überwacht werden soll.",
        ]
    else:
        executive_summary = (
            f"This Validation compares the new Deep Scan {validation_scan.scan_id} with Full Assessment baseline "
            f"{baseline_scan.scan_id}. The Data Health Score changed by {score_delta:+d} points to "
            f"{validation_score}/100. {len(buckets['resolved'])} findings were resolved, "
            f"{len(buckets['improved'])} improved, and {len(buckets['new'])} new findings were detected."
        )
        next_steps = [
            "Review and prioritize new or regressed findings first.",
            "Close remaining high-impact findings in the next remediation wave.",
            "Use Monitoring if data quality should be controlled continuously after Validation.",
        ]

    return ValidationReport(
        report_id=f"validation-{validation_scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        baseline_scan_id=baseline_scan.scan_id,
        baseline_reference_source=baseline_reference_source,
        validation_scan_id=validation_scan.scan_id,
        generated_at_utc=datetime.now(timezone.utc),
        baseline_generated_at_utc=baseline_scan.generated_at_utc,
        validation_generated_at_utc=validation_scan.generated_at_utc,
        company_label=tenant.tenant_id,
        environment_label=tenant.environment_name,
        baseline_score=baseline_score,
        validation_score=validation_score,
        score_delta=score_delta,
        baseline_issues_count=baseline_issues,
        validation_issues_count=validation_issues,
        issues_delta=validation_issues - baseline_issues,
        baseline_affected_records=baseline_affected,
        validation_affected_records=validation_affected,
        affected_records_delta=validation_affected - baseline_affected,
        baseline_estimated_loss_eur=baseline_loss,
        validation_estimated_loss_eur=validation_loss,
        estimated_loss_delta_eur=loss_delta,
        business_impact_delta_eur=loss_delta,
        estimated_exposure_reduction_eur=exposure_reduction,
        resolved_count=len(buckets["resolved"]),
        improved_count=len(buckets["improved"]),
        remaining_count=len(buckets["remaining"]),
        regressed_count=len(buckets["regressed"]),
        new_count=len(buckets["new"]),
        executive_summary=executive_summary,
        management_interpretation=[],
        business_areas=business_areas,
        resolved=buckets["resolved"],
        improved=buckets["improved"],
        remaining=buckets["remaining"],
        regressed=buckets["regressed"],
        new_findings=buckets["new"],
        next_steps=next_steps,
    )
