"""Verified scan references for BCSentinel Validation v2.

Select *two* independent references: the original confirmed Full/Free baseline
and the most recent comparable completed prior scan. Never invent scope or
upgrade an incomplete scan to a confirmed baseline.
"""
from __future__ import annotations

from dataclasses import dataclass
from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.assessment_scope_models import AssessmentScopeSnapshot
from app.models import Scan, ScanRunStatus, Tenant
from app.services.assessment_scope_service import (
    get_latest_confirmed_scope, get_latest_scope, included_module_codes,
)
from app.services.scan_company_service import canonical_company_id


@dataclass(frozen=True)
class ComparisonReference:
    initial: Scan
    previous: Scan
    current: Scan
    scope_version: int


def _unavailable(message: str) -> None:
    raise HTTPException(status_code=409, detail=f"Validation evidence unavailable: {message}")


def _company(scan: Scan) -> str:
    if not scan.bc_company_id:
        _unavailable("verified BC company missing")
    try:
        return canonical_company_id(scan.bc_company_id)
    except (ValueError, TypeError):
        _unavailable("verified BC company invalid")


def _same_company_currency(scan: Scan, current: Scan) -> bool:
    return (
        bool(scan.bc_company_id and current.bc_company_id)
        and _company(scan) == _company(current)
        and str(scan.lcy_code or "").strip().upper() == "EUR"
        and str(current.lcy_code or "").strip().upper() == "EUR"
    )


def _persisted_completed(db: Session, scan: Scan) -> bool:
    return db.scalar(select(ScanRunStatus.id).where(
        ScanRunStatus.run_id == scan.scan_id,
        ScanRunStatus.tenant_id == scan.tenant_id,
        ScanRunStatus.status.in_(["completed", "completed_with_warnings"]),
        ScanRunStatus.result_persisted_at_utc.is_not(None),
    ).limit(1)) is not None


def _earlier(scan: Scan, current: Scan) -> bool:
    return (
        scan.generated_at_utc < current.generated_at_utc
        or (scan.generated_at_utc == current.generated_at_utc and scan.id < current.id)
    )


def choose_validation_references(
    db: Session, tenant: Tenant, current: Scan
) -> ComparisonReference:
    if current.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=404, detail="Validation report not found.")
    _company(current)
    if not _persisted_completed(db, current):
        _unavailable("current scan not completed and persisted")
    if str(current.lcy_code or "").upper() != "EUR":
        _unavailable("verified EUR local currency missing")
    current_scope = get_latest_scope(db, current.scan_id)
    if current_scope is None or current_scope.tenant_id != tenant.tenant_id:
        _unavailable("current scan scope snapshot missing")
    if not current_scope.modules:
        _unavailable("current scan module scope missing")

    prior = list(db.scalars(select(Scan).where(
        Scan.tenant_id == tenant.tenant_id,
        Scan.scan_id != current.scan_id,
        or_(
            Scan.generated_at_utc < current.generated_at_utc,
            and_(
                Scan.generated_at_utc == current.generated_at_utc,
                Scan.id < current.id,
            ),
        ),
    ).order_by(Scan.generated_at_utc.desc(), Scan.id.desc())).all())

    compatible: list[Scan] = []
    current_modules = included_module_codes(current_scope)
    if not current_modules:
        _unavailable("current included modules missing")
    for candidate in prior:
        if not _persisted_completed(db, candidate):
            continue
        if not _earlier(candidate, current) or not _same_company_currency(candidate, current):
            continue
        scope = get_latest_scope(db, candidate.scan_id)
        if (
            scope is None or scope.tenant_id != tenant.tenant_id
            or not scope.modules or included_module_codes(scope) != current_modules
        ):
            continue
        compatible.append(candidate)

    initial: Scan | None = None
    confirmed_version: int | None = None
    # Chronologically first explicitly CONFIRMED comparable baseline,
    # and never a Validation scan itself.
    from app.services.product_license_service import PRODUCT_VALIDATION_CHECK
    from app.models import TenantScanCredit
    for candidate in reversed(compatible):
        confirmed = get_latest_confirmed_scope(db, candidate.scan_id)
        if confirmed is None or confirmed.tenant_id != tenant.tenant_id:
            continue
        if included_module_codes(confirmed) != current_modules:
            continue
        validation_credit = db.scalar(select(TenantScanCredit.id).where(
            TenantScanCredit.tenant_id == tenant.tenant_id,
            TenantScanCredit.product_code == PRODUCT_VALIDATION_CHECK,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == candidate.scan_id,
        ).limit(1))
        if validation_credit is not None:
            continue
        initial = candidate
        confirmed_version = confirmed.version
        break
    if initial is None or confirmed_version is None:
        _unavailable("original confirmed Assessment baseline missing or incompatible")
    # Any earlier scan before the initial baseline cannot be a comparison
    # reference; the most recent compatible scan AFTER baseline is preferred.
    eligible = [scan for scan in compatible if
                scan.generated_at_utc > initial.generated_at_utc or (
                    scan.generated_at_utc == initial.generated_at_utc and scan.id >= initial.id)]
    previous = eligible[0] if eligible else initial
    return ComparisonReference(
        initial=initial, previous=previous, current=current,
        scope_version=confirmed_version,
    )
