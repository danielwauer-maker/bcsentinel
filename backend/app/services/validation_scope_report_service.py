from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment_scope_models import AssessmentScopeSnapshot, ValidationScopeBinding
from app.models import Scan, Tenant
from app.schemas.validation_report import ValidationFindingDelta, ValidationReport
from app.services.assessment_scope_service import (
    SUPPORTED_STANDARD_MODULES,
    get_latest_confirmed_scope,
    included_module_codes,
)
from app.services.validation_report_service import build_validation_report as build_base_validation_report

AREA_TO_MODULE = {
    "finance": "finance",
    "sales": "sales",
    "purchasing": "purchasing",
    "inventory": "inventory",
    "crm": "crm",
    "manufacturing": "manufacturing",
    "service": "service",
    "jobs": "jobs",
    "hr": "hr",
    "system": "system",
}


def _module_for_category(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return AREA_TO_MODULE.get(normalized, "system")


def _binding_scope(db: Session, report: ValidationReport) -> AssessmentScopeSnapshot | None:
    binding = db.scalar(
        select(ValidationScopeBinding).where(
            ValidationScopeBinding.validation_scan_id == report.validation_scan_id,
            ValidationScopeBinding.tenant_id == report.tenant_id,
        )
    )
    if binding is not None:
        return db.scalar(
            select(AssessmentScopeSnapshot).where(
                AssessmentScopeSnapshot.id == binding.scope_snapshot_id,
                AssessmentScopeSnapshot.scan_id == binding.baseline_scan_id,
                AssessmentScopeSnapshot.version == binding.scope_version,
                AssessmentScopeSnapshot.state == "confirmed",
            )
        )

    scope = get_latest_confirmed_scope(db, report.baseline_scan_id)
    if scope is None:
        # Backward compatibility: historical Validation reports created before
        # Assessment Scope v1 keep their legacy whole-scan semantics.
        return None

    binding = ValidationScopeBinding(
        tenant_id=report.tenant_id,
        validation_scan_id=report.validation_scan_id,
        baseline_scan_id=report.baseline_scan_id,
        scope_snapshot_id=scope.id,
        scope_version=scope.version,
        bound_at_utc=datetime.now(timezone.utc),
    )
    db.add(binding)
    db.commit()
    return scope


def _validation_score(validation_scan: Scan, included: set[str], fallback: int) -> int:
    values: list[int] = []
    for module_code in included:
        config = SUPPORTED_STANDARD_MODULES.get(module_code)
        if config is None:
            continue
        _label, attr = config
        try:
            value = int(getattr(validation_scan, attr, 100))
        except (TypeError, ValueError):
            value = 100
        values.append(max(0, min(100, value)))
    if not values:
        return max(0, min(100, int(fallback or 0)))
    return int((sum(values) / len(values)) + 0.5)


def _filter_findings(rows: list[ValidationFindingDelta], included: set[str]) -> list[ValidationFindingDelta]:
    return [row for row in rows if _module_for_category(row.category) in included]


def _affected_before(groups: list[list[ValidationFindingDelta]]) -> int:
    return sum(max(0, int(row.affected_before or 0)) for group in groups for row in group)


def _affected_after(groups: list[list[ValidationFindingDelta]]) -> int:
    return sum(max(0, int(row.affected_after or 0)) for group in groups for row in group)


def _impact_before(groups: list[list[ValidationFindingDelta]]) -> float:
    return round(sum(max(0.0, float(row.impact_before_eur or 0.0)) for group in groups for row in group), 2)


def _impact_after(groups: list[list[ValidationFindingDelta]]) -> float:
    return round(sum(max(0.0, float(row.impact_after_eur or 0.0)) for group in groups for row in group), 2)


def build_validation_report(db: Session, tenant: Tenant, validation_scan_id: str) -> ValidationReport:
    base = build_base_validation_report(db, tenant, validation_scan_id)
    scope = _binding_scope(db, base)
    if scope is None:
        return base

    included = included_module_codes(scope)
    validation_scan = db.scalar(
        select(Scan).where(
            Scan.scan_id == base.validation_scan_id,
            Scan.tenant_id == tenant.tenant_id,
        )
    )
    if validation_scan is None:
        return base

    resolved = _filter_findings(base.resolved, included)
    improved = _filter_findings(base.improved, included)
    remaining = _filter_findings(base.remaining, included)
    regressed = _filter_findings(base.regressed, included)
    new_findings = _filter_findings(base.new_findings, included)

    baseline_groups = [resolved, improved, remaining, regressed]
    validation_groups = [improved, remaining, regressed, new_findings]
    baseline_issues = sum(len(group) for group in baseline_groups)
    validation_issues = sum(len(group) for group in validation_groups)
    baseline_affected = _affected_before(baseline_groups)
    validation_affected = _affected_after(validation_groups)
    baseline_loss = _impact_before(baseline_groups)
    validation_loss = _impact_after(validation_groups)

    baseline_score = int(scope.score_value)
    validation_score = _validation_score(validation_scan, included, base.validation_score)
    score_delta = validation_score - baseline_score
    issues_delta = validation_issues - baseline_issues
    affected_delta = validation_affected - baseline_affected
    loss_delta = round(validation_loss - baseline_loss, 2)
    exposure_reduction = round(max(0.0, baseline_loss - validation_loss), 2)

    business_areas = [
        row for row in base.business_areas if _module_for_category(row.name) in included
    ]

    if base.language == "de":
        executive_summary = (
            f"Validation gegen bestätigte Full-Assessment-Baseline v{scope.version}: "
            f"Health Score {baseline_score}/100 → {validation_score}/100 ({score_delta:+d}). "
            f"Findings {baseline_issues} → {validation_issues} ({issues_delta:+d}). "
            "Der Vergleich verwendet denselben bestätigten Business-Central-Standard-Scope; Drittanbieter- und Custom-Logik bleibt außerhalb des Scores."
        )
        interpretation = [
            f"Die gemessene Score-Veränderung beträgt {score_delta:+d} Punkte innerhalb desselben bestätigten Scopes.",
            f"Der modellierte Business Impact verändert sich um {loss_delta:+.0f} EUR; dies ist kein Nachweis realisierter Einsparungen.",
        ]
    else:
        executive_summary = (
            f"Validation against confirmed Full Assessment baseline v{scope.version}: "
            f"Health Score {baseline_score}/100 → {validation_score}/100 ({score_delta:+d}). "
            f"Findings {baseline_issues} → {validation_issues} ({issues_delta:+d}). "
            "The comparison uses the same confirmed Business Central standard scope; third-party and custom logic remains outside the score."
        )
        interpretation = [
            f"Measured score change is {score_delta:+d} points within the same confirmed scope.",
            f"Modeled Business Impact changes by {loss_delta:+.0f} EUR; this is not evidence of realized savings.",
        ]

    return base.model_copy(
        update={
            "baseline_reference_source": f"{base.baseline_reference_source}+confirmed_scope_v{scope.version}",
            "baseline_score": baseline_score,
            "validation_score": validation_score,
            "score_delta": score_delta,
            "baseline_issues_count": baseline_issues,
            "validation_issues_count": validation_issues,
            "issues_delta": issues_delta,
            "baseline_affected_records": baseline_affected,
            "validation_affected_records": validation_affected,
            "affected_records_delta": affected_delta,
            "baseline_estimated_loss_eur": baseline_loss,
            "validation_estimated_loss_eur": validation_loss,
            "estimated_loss_delta_eur": loss_delta,
            "business_impact_delta_eur": loss_delta,
            "estimated_exposure_reduction_eur": exposure_reduction,
            "resolved_count": len(resolved),
            "improved_count": len(improved),
            "remaining_count": len(remaining),
            "regressed_count": len(regressed),
            "new_count": len(new_findings),
            "executive_summary": executive_summary,
            "management_interpretation": interpretation,
            "business_areas": business_areas,
            "resolved": resolved,
            "improved": improved,
            "remaining": remaining,
            "regressed": regressed,
            "new_findings": new_findings,
        }
    )
