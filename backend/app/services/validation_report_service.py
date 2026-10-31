from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Scan, ScanIssueRecord, Tenant, TenantScanCredit
from app.schemas.validation_report import ValidationFindingDelta, ValidationReport
from app.services.localization_service import tenant_language
from app.services.product_license_service import PRODUCT_VALIDATION_CHECK

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


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


def _normalize_category(value: str | None) -> str:
    return str(value or "System").strip() or "System"


def _load_validation_scan(db: Session, tenant: Tenant, validation_scan_id: str) -> Scan:
    scan = db.scalar(
        select(Scan).where(
            Scan.scan_id == validation_scan_id,
            Scan.tenant_id == tenant.tenant_id,
        )
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Validation report not found.")

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
    return scan


def _load_baseline_scan(db: Session, tenant: Tenant, validation_scan: Scan) -> Scan:
    baseline = db.scalar(
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
        .limit(1)
    )
    if baseline is None:
        raise HTTPException(status_code=409, detail="Validation requires an earlier Assessment/baseline scan.")
    return baseline


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

    before_severity = SEVERITY_RANK.get(str(before.severity or "").lower(), 0)
    after_severity = SEVERITY_RANK.get(str(after.severity or "").lower(), 0)
    before_affected = _safe_int(before.affected_count)
    after_affected = _safe_int(after.affected_count)
    before_impact = _safe_float(before.estimated_impact_eur)
    after_impact = _safe_float(after.estimated_impact_eur)

    if after_severity > before_severity or after_affected > before_affected or after_impact > before_impact + 0.01:
        return "regressed"
    if after_severity < before_severity or after_affected < before_affected or after_impact < before_impact - 0.01:
        return "improved"
    return "remaining"


def _delta(before: ScanIssueRecord | None, after: ScanIssueRecord | None, status: str) -> ValidationFindingDelta:
    source = after or before
    assert source is not None
    return ValidationFindingDelta(
        code=source.code,
        title=source.title,
        category=_normalize_category(source.category),
        severity_before=str(before.severity or "").lower() if before else None,
        severity_after=str(after.severity or "").lower() if after else None,
        affected_before=max(0, _safe_int(before.affected_count)) if before else 0,
        affected_after=max(0, _safe_int(after.affected_count)) if after else 0,
        impact_before_eur=round(_safe_float(before.estimated_impact_eur), 2) if before else 0.0,
        impact_after_eur=round(_safe_float(after.estimated_impact_eur), 2) if after else 0.0,
        status=status,
    )


def build_validation_report(db: Session, tenant: Tenant, validation_scan_id: str) -> ValidationReport:
    language = tenant_language(tenant)
    validation_scan = _load_validation_scan(db, tenant, validation_scan_id)
    baseline_scan = _load_baseline_scan(db, tenant, validation_scan)

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
        buckets[status].append(_delta(before, after, status))

    baseline_score = max(0, min(100, _safe_int(baseline_scan.data_score)))
    validation_score = max(0, min(100, _safe_int(validation_scan.data_score)))
    baseline_loss = round(_safe_float(baseline_scan.estimated_loss_eur), 2)
    validation_loss = round(_safe_float(validation_scan.estimated_loss_eur), 2)
    score_delta = validation_score - baseline_score
    loss_delta = round(validation_loss - baseline_loss, 2)
    exposure_reduction = round(max(0.0, baseline_loss - validation_loss), 2)

    if language == "de":
        executive_summary = (
            f"Die Validierung vergleicht den neuen Deep Scan {validation_scan.scan_id} mit der vorherigen Baseline "
            f"{baseline_scan.scan_id}. Der Data Health Score verändert sich um {score_delta:+d} Punkte auf "
            f"{validation_score}/100. {len(buckets['resolved'])} Findings wurden behoben, "
            f"{len(buckets['improved'])} verbessert und {len(buckets['new'])} neu erkannt."
        )
        next_steps = [
            "Prüfe zuerst neue oder verschlechterte Findings und weise klare Owner zu.",
            "Schließe verbleibende High-Impact-Findings in der nächsten Bereinigungswelle.",
            "Nutze Monitoring, wenn die Datenqualität nach der Validierung kontinuierlich überwacht werden soll.",
        ]
    else:
        executive_summary = (
            f"This Validation compares the new Deep Scan {validation_scan.scan_id} with baseline "
            f"{baseline_scan.scan_id}. The Data Health Score changed by {score_delta:+d} points to "
            f"{validation_score}/100. {len(buckets['resolved'])} findings were resolved, "
            f"{len(buckets['improved'])} improved, and {len(buckets['new'])} new findings were detected."
        )
        next_steps = [
            "Review new or regressed findings first and assign clear remediation owners.",
            "Close the remaining high-impact findings in the next remediation wave.",
            "Use Monitoring if data quality should be controlled continuously after Validation.",
        ]

    return ValidationReport(
        report_id=f"validation-{validation_scan.scan_id}",
        tenant_id=tenant.tenant_id,
        language=language,
        baseline_scan_id=baseline_scan.scan_id,
        validation_scan_id=validation_scan.scan_id,
        generated_at_utc=datetime.now(timezone.utc),
        baseline_generated_at_utc=baseline_scan.generated_at_utc,
        validation_generated_at_utc=validation_scan.generated_at_utc,
        company_label=tenant.tenant_id,
        environment_label=tenant.environment_name,
        baseline_score=baseline_score,
        validation_score=validation_score,
        score_delta=score_delta,
        baseline_issues_count=max(0, _safe_int(baseline_scan.issues_count)),
        validation_issues_count=max(0, _safe_int(validation_scan.issues_count)),
        issues_delta=_safe_int(validation_scan.issues_count) - _safe_int(baseline_scan.issues_count),
        baseline_estimated_loss_eur=baseline_loss,
        validation_estimated_loss_eur=validation_loss,
        estimated_loss_delta_eur=loss_delta,
        estimated_exposure_reduction_eur=exposure_reduction,
        resolved_count=len(buckets["resolved"]),
        improved_count=len(buckets["improved"]),
        remaining_count=len(buckets["remaining"]),
        regressed_count=len(buckets["regressed"]),
        new_count=len(buckets["new"]),
        executive_summary=executive_summary,
        resolved=buckets["resolved"],
        improved=buckets["improved"],
        remaining=buckets["remaining"],
        regressed=buckets["regressed"],
        new_findings=buckets["new"],
        next_steps=next_steps,
    )
