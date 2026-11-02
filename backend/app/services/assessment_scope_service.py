from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.assessment_scope_models import AssessmentScopeModule, AssessmentScopeSnapshot
from app.models import Scan, ScanIssueRecord

SUPPORTED_STANDARD_MODULES = {
    "system": ("System", "system_score"),
    "finance": ("Finance", "finance_score"),
    "sales": ("Sales", "sales_score"),
    "purchasing": ("Purchasing", "purchasing_score"),
    "inventory": ("Inventory", "inventory_score"),
    "crm": ("CRM", "crm_score"),
    "manufacturing": ("Manufacturing", "manufacturing_score"),
    "service": ("Service", "service_score"),
    "jobs": ("Jobs", "jobs_score"),
    "hr": ("HR", "hr_score"),
}

ISSUE_AREA_ALIASES = {
    "purchase": "purchasing",
    "purchasing": "purchasing",
    "vendor": "purchasing",
    "inventory": "inventory",
    "item": "inventory",
    "customer": "crm",
    "crm": "crm",
    "job": "jobs",
    "jobs": "jobs",
    "project": "jobs",
    "projects": "jobs",
    "finance": "finance",
    "sales": "sales",
    "manufacturing": "manufacturing",
    "service": "service",
    "hr": "hr",
    "system": "system",
}


def _bounded_int(value: object, default: int = 100) -> int:
    try:
        parsed = default if value is None else int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0, min(100, parsed))


def _score(scan: Scan, attr: str) -> int:
    return _bounded_int(getattr(scan, attr, None), 100)


def _positive(*values: object) -> bool:
    return any(int(value or 0) > 0 for value in values)


def _profile_has_usage_evidence(scan: Scan) -> bool:
    return _positive(
        scan.customers_count,
        scan.vendors_count,
        scan.items_count,
        scan.customer_ledger_entries_count,
        scan.vendor_ledger_entries_count,
        scan.item_ledger_entries_count,
        scan.sales_headers_count,
        scan.sales_lines_count,
        scan.purchase_headers_count,
        scan.purchase_lines_count,
        scan.gl_entries_count,
        scan.value_entries_count,
        scan.warehouse_entries_count,
    )


def _legacy_enabled_modules(scan: Scan) -> set[str]:
    aliases = {
        "purchase": "purchasing",
        "purchasing": "purchasing",
        "job": "jobs",
        "jobs": "jobs",
        "project": "jobs",
        "projects": "jobs",
    }
    result: set[str] = set()
    for raw in str(scan.enabled_modules or "").split(","):
        normalized = raw.strip().lower()
        if not normalized:
            continue
        normalized = aliases.get(normalized, normalized)
        if normalized in SUPPORTED_STANDARD_MODULES:
            result.add(normalized)
    return result


def _usage_detection(scan: Scan, module_code: str) -> tuple[str, float, str]:
    if module_code == "system":
        return "active", 1.0, "Core Business Central system/setup area."
    if module_code == "finance":
        if _positive(scan.gl_entries_count):
            return "active", 0.98, "General Ledger activity detected."
        return "not_detected", 0.90, "No General Ledger activity detected in the scan profile."
    if module_code == "sales":
        if _positive(scan.customers_count, scan.customer_ledger_entries_count, scan.sales_headers_count, scan.sales_lines_count):
            return "active", 0.98, "Customer or sales transaction activity detected."
        return "not_detected", 0.92, "No customer or sales transaction activity detected."
    if module_code == "purchasing":
        if _positive(scan.vendors_count, scan.vendor_ledger_entries_count, scan.purchase_headers_count, scan.purchase_lines_count):
            return "active", 0.98, "Vendor or purchasing transaction activity detected."
        return "not_detected", 0.92, "No vendor or purchasing transaction activity detected."
    if module_code == "inventory":
        if _positive(scan.items_count, scan.item_ledger_entries_count, scan.value_entries_count, scan.warehouse_entries_count):
            return "active", 0.98, "Item, inventory, value or warehouse activity detected."
        return "not_detected", 0.92, "No item, inventory, value or warehouse activity detected."
    return "unknown", 0.0, "Current scan profile has no reliable usage signal for this standard area."


def _weighted_score(modules: Iterable[AssessmentScopeModule], fallback: int) -> int:
    included = [module.module_score for module in modules if bool(module.included_in_score)]
    if not included:
        return _bounded_int(fallback, 100)
    return int(round(sum(included) / len(included)))


def _next_version(db: Session, scan_id: str) -> int:
    value = db.scalar(select(func.max(AssessmentScopeSnapshot.version)).where(AssessmentScopeSnapshot.scan_id == scan_id))
    return int(value or 0) + 1


def get_latest_scope(db: Session, scan_id: str) -> AssessmentScopeSnapshot | None:
    return db.scalar(
        select(AssessmentScopeSnapshot)
        .where(AssessmentScopeSnapshot.scan_id == scan_id)
        .order_by(AssessmentScopeSnapshot.version.desc())
    )


def get_or_create_auto_scope(db: Session, scan: Scan) -> AssessmentScopeSnapshot:
    existing = db.scalar(
        select(AssessmentScopeSnapshot)
        .where(AssessmentScopeSnapshot.scan_id == scan.scan_id, AssessmentScopeSnapshot.state == "auto")
        .order_by(AssessmentScopeSnapshot.version.desc())
    )
    if existing is not None:
        return existing

    fallback_score = _bounded_int(scan.data_score, 100)
    has_usage_evidence = _profile_has_usage_evidence(scan)
    legacy_enabled = _legacy_enabled_modules(scan)
    legacy_mode = not has_usage_evidence

    snapshot = AssessmentScopeSnapshot(
        scan_id=scan.scan_id,
        tenant_id=scan.tenant_id,
        version=_next_version(db, scan.scan_id),
        state="auto",
        source="legacy_scan_contract" if legacy_mode else "usage_detection",
        score_type="preliminary",
        score_value=fallback_score,
        supported_modules_count=len(SUPPORTED_STANDARD_MODULES),
        included_modules_count=0,
        unknown_modules_count=0,
        unsupported_extensions_json="[]",
        created_at_utc=datetime.now(timezone.utc),
        confirmed_at_utc=None,
    )
    db.add(snapshot)
    db.flush()

    module_rows: list[AssessmentScopeModule] = []
    for module_code, (display_name, score_attr) in SUPPORTED_STANDARD_MODULES.items():
        if legacy_mode:
            # Historical scans predate reliable usage counters. Preserve their
            # stored score and, when present, their legacy enabled-module list.
            included = module_code in legacy_enabled if legacy_enabled else True
            detection_status = "active" if included else "not_detected"
            confidence = 0.5
            reason = "Legacy scan compatibility: usage profile was not available."
        else:
            detection_status, confidence, reason = _usage_detection(scan, module_code)
            included = detection_status == "active"

        row = AssessmentScopeModule(
            snapshot_id=snapshot.id,
            module_code=module_code,
            display_name=display_name,
            support_status="supported",
            detection_status=detection_status,
            decision="inherit",
            included_in_score=1 if included else 0,
            confidence=confidence,
            detection_reason=reason,
            module_score=_score(scan, score_attr),
        )
        db.add(row)
        module_rows.append(row)

    snapshot.included_modules_count = sum(bool(row.included_in_score) for row in module_rows)
    snapshot.unknown_modules_count = sum(row.detection_status == "unknown" for row in module_rows)
    snapshot.score_value = fallback_score if legacy_mode else _weighted_score(module_rows, fallback_score)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def confirm_scope(db: Session, scan: Scan, decisions: dict[str, str]) -> AssessmentScopeSnapshot:
    auto_scope = get_or_create_auto_scope(db, scan)
    normalized = {str(key).strip().lower(): str(value).strip().lower() for key, value in decisions.items()}
    unknown_codes = sorted(set(normalized).difference(SUPPORTED_STANDARD_MODULES))
    if unknown_codes:
        raise HTTPException(status_code=422, detail=f"Unsupported scope modules: {', '.join(unknown_codes)}")
    invalid_values = sorted({value for value in normalized.values() if value not in {"include", "exclude", "inherit"}})
    if invalid_values:
        raise HTTPException(status_code=422, detail="Scope decisions must be include, exclude or inherit.")
    if normalized.get("system") == "exclude":
        raise HTTPException(status_code=422, detail="The core System area cannot be excluded from the confirmed baseline.")

    snapshot = AssessmentScopeSnapshot(
        scan_id=scan.scan_id,
        tenant_id=scan.tenant_id,
        version=_next_version(db, scan.scan_id),
        state="confirmed",
        source="customer_confirmation",
        score_type="confirmed_baseline",
        score_value=auto_scope.score_value,
        supported_modules_count=len(SUPPORTED_STANDARD_MODULES),
        included_modules_count=0,
        unknown_modules_count=0,
        unsupported_extensions_json=auto_scope.unsupported_extensions_json or "[]",
        created_at_utc=datetime.now(timezone.utc),
        confirmed_at_utc=datetime.now(timezone.utc),
    )
    db.add(snapshot)
    db.flush()

    auto_by_code = {row.module_code: row for row in auto_scope.modules}
    rows: list[AssessmentScopeModule] = []
    for module_code, (display_name, _score_attr) in SUPPORTED_STANDARD_MODULES.items():
        auto_row = auto_by_code[module_code]
        decision = normalized.get(module_code, "inherit")
        if module_code == "system":
            included = True
            decision = "include"
        elif decision == "include":
            included = True
        elif decision == "exclude":
            included = False
        else:
            included = bool(auto_row.included_in_score)
        row = AssessmentScopeModule(
            snapshot_id=snapshot.id,
            module_code=module_code,
            display_name=display_name,
            support_status="supported",
            detection_status=auto_row.detection_status,
            decision=decision,
            included_in_score=1 if included else 0,
            confidence=auto_row.confidence,
            detection_reason=auto_row.detection_reason,
            module_score=auto_row.module_score,
        )
        db.add(row)
        rows.append(row)

    snapshot.included_modules_count = sum(bool(row.included_in_score) for row in rows)
    snapshot.unknown_modules_count = sum(row.detection_status == "unknown" and row.decision == "inherit" for row in rows)
    snapshot.score_value = _weighted_score(rows, auto_scope.score_value)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def supported_issue_area(issue: ScanIssueRecord) -> str:
    raw = str(issue.category or "").strip().lower()
    code = str(issue.code or "").upper()
    if raw in ISSUE_AREA_ALIASES:
        return ISSUE_AREA_ALIASES[raw]
    if code.startswith(("CUSTOMER", "CUSTOMERS")):
        return "crm"
    if code.startswith(("VENDOR", "VENDORS", "PURCHASE", "PURCH")):
        return "purchasing"
    if code.startswith(("ITEM", "ITEMS", "INVENTORY", "WAREHOUSE", "VALUE")):
        return "inventory"
    if code.startswith(("SALE", "SALES")):
        return "sales"
    if "LEDGER" in code or code.startswith(("GL_", "G_L_")):
        return "finance"
    return "system"


def included_module_codes(scope: AssessmentScopeSnapshot) -> set[str]:
    return {row.module_code for row in scope.modules if bool(row.included_in_score)}


def serialize_scope(scope: AssessmentScopeSnapshot, *, include_modules: bool) -> dict:
    payload = {
        "scan_id": scope.scan_id,
        "version": scope.version,
        "state": scope.state,
        "score_type": scope.score_type,
        "score": scope.score_value,
        "supported_modules": scope.supported_modules_count,
        "included_modules": scope.included_modules_count,
        "unknown_modules": scope.unknown_modules_count,
        "custom_extensions_scored": False,
        "unsupported_extensions": json.loads(scope.unsupported_extensions_json or "[]"),
        "confirmed_at_utc": scope.confirmed_at_utc,
    }
    if include_modules:
        payload["modules"] = [
            {
                "module_code": row.module_code,
                "display_name": row.display_name,
                "support_status": row.support_status,
                "detection_status": row.detection_status,
                "decision": row.decision,
                "included_in_score": bool(row.included_in_score),
                "confidence": row.confidence,
                "detection_reason": row.detection_reason,
                "module_score": row.module_score,
            }
            for row in sorted(scope.modules, key=lambda item: item.module_code)
        ]
    return payload
