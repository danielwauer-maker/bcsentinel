from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import CreditLedgerEntry, Scan, ScanRunStatus, ScanStartRequest, Tenant, TenantScanCredit
from app.services.product_license_service import (
    PRODUCT_FULL_ANALYSIS,
    PRODUCT_VALIDATION_CHECK,
    MONITORING_PRODUCTS,
    active_entitlement_product_codes,
    has_active_monitoring_subscription,
    product_code_storage_aliases,
    scan_credit_count,
)
from app.services.scan_status_service import create_or_get_scan_run


class ScanStartConflictError(ValueError):
    pass


class ScanCreditUnavailableError(ValueError):
    pass


class MonitoringInactiveError(ValueError):
    pass


class FreeScanAlreadyUsedError(ValueError):
    pass


@dataclass(frozen=True)
class ScanStartResult:
    scan_id: str
    scan_mode: str
    product_code: str | None
    credit_consumed: bool
    idempotent_replay: bool
    execution_token: str
    correlation_id: str


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_client_request_id(value: str) -> str:
    try:
        return str(UUID((value or "").strip().strip("{}"))).lower()
    except (ValueError, AttributeError) as exc:
        raise ValueError("client_request_id must be a valid GUID.") from exc


def normalize_requested_scan_mode(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    aliases = {
        "full_analysis": "assessment",
        "premium_deep": "deep",
        "free_data_health_score": "data_health_score",
        "health_score": "data_health_score",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"assessment", "validation", "validation_check", "monitoring", "deep", "data_health_score"}:
        raise ValueError("scan_mode must be assessment, validation, monitoring, deep, or data_health_score.")
    return "validation" if normalized == "validation_check" else normalized


def build_payload_hash(*, run_id: str, scan_mode: str, total_modules: int, company_name: str | None, environment_name: str | None) -> str:
    canonical = json.dumps(
        {
            "run_id": (run_id or "").strip(),
            "scan_mode": normalize_requested_scan_mode(scan_mode),
            "total_modules": max(int(total_modules or 0), 0),
            "company_name": (company_name or "").strip(),
            "environment_name": (environment_name or "").strip(),
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _result_from_request(db: Session, request: ScanStartRequest, *, replay: bool) -> ScanStartResult:
    run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == request.scan_id))
    if run is None or not run.lease_token:
        raise RuntimeError("Accepted scan start is missing its lifecycle execution token.")
    return ScanStartResult(
        scan_id=request.scan_id,
        scan_mode=request.requested_scan_mode,
        product_code=request.resolved_product_code,
        credit_consumed=request.credit_id is not None,
        idempotent_replay=replay,
        execution_token=run.lease_token,
        correlation_id=run.correlation_id or "",
    )


def _existing_result(db: Session, *, tenant_id: str, client_request_id: str, payload_hash: str) -> ScanStartResult | None:
    request = db.scalar(
        select(ScanStartRequest).where(
            ScanStartRequest.tenant_id == tenant_id,
            ScanStartRequest.client_request_id == client_request_id,
        )
    )
    if request is None:
        return None
    if request.payload_hash != payload_hash:
        raise ScanStartConflictError(
            "This client_request_id was already used with a different scan payload. Reuse the original payload or start a new scan."
        )
    return _result_from_request(db, request, replay=True)


def _claim_credit(db: Session, *, tenant_id: str, scan_id: str, product_codes: set[str] | None) -> TenantScanCredit | None:
    conditions = [
        TenantScanCredit.tenant_id == tenant_id,
        TenantScanCredit.status == "available",
    ]
    if product_codes is not None:
        conditions.append(TenantScanCredit.product_code.in_(sorted(product_codes)))

    candidate = db.scalar(
        select(TenantScanCredit)
        .where(*conditions)
        .order_by(TenantScanCredit.created_at_utc.asc(), TenantScanCredit.id.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    if candidate is None:
        return None

    claimed = db.execute(
        update(TenantScanCredit)
        .where(TenantScanCredit.id == candidate.id, TenantScanCredit.status == "available")
        .values(status="consumed", consumed_scan_id=scan_id, consumed_at_utc=_now())
    )
    if claimed.rowcount != 1:
        return None
    db.flush()
    db.refresh(candidate)
    return candidate


def _resolve_access_and_credit(db: Session, *, tenant: Tenant, requested_mode: str, scan_id: str) -> tuple[str | None, TenantScanCredit | None]:
    monitoring_active = has_active_monitoring_subscription(db, tenant) or bool(
        set(active_entitlement_product_codes(db, tenant.tenant_id)).intersection(MONITORING_PRODUCTS)
    )
    if requested_mode == "data_health_score":
        return None, None
    if requested_mode == "monitoring":
        if not monitoring_active:
            raise MonitoringInactiveError("An active Monitoring subscription is required for this scan.")
        return "monitoring", None
    if requested_mode == "assessment":
        product = PRODUCT_FULL_ANALYSIS
        credit = _claim_credit(db, tenant_id=tenant.tenant_id, scan_id=scan_id, product_codes=product_code_storage_aliases(product))
    elif requested_mode == "validation":
        product = PRODUCT_VALIDATION_CHECK
        credit = _claim_credit(db, tenant_id=tenant.tenant_id, scan_id=scan_id, product_codes={product})
    else:
        if monitoring_active:
            return "monitoring", None
        product = "legacy_deep"
        credit = _claim_credit(db, tenant_id=tenant.tenant_id, scan_id=scan_id, product_codes=None)
        if credit is not None:
            product = credit.product_code
    if credit is None:
        raise ScanCreditUnavailableError(
            "No matching scan credit is available. Purchase the required product or start Monitoring, then retry with the same request ID."
        )
    return product, credit


def accept_scan_start(
    db: Session,
    *,
    tenant: Tenant,
    client_request_id: str,
    run_id: str,
    scan_mode: str,
    total_modules: int,
    company_name: str | None,
    environment_name: str | None,
) -> ScanStartResult:
    request_id = normalize_client_request_id(client_request_id)
    requested_mode = normalize_requested_scan_mode(scan_mode)
    normalized_run_id = (run_id or "").strip()
    if not normalized_run_id or len(normalized_run_id) > 50:
        raise ValueError("run_id is required and must not exceed 50 characters.")
    payload_hash = build_payload_hash(
        run_id=normalized_run_id,
        scan_mode=requested_mode,
        total_modules=total_modules,
        company_name=company_name,
        environment_name=environment_name,
    )
    replay = _existing_result(
        db, tenant_id=tenant.tenant_id, client_request_id=request_id, payload_hash=payload_hash
    )
    if replay is not None:
        db.commit()
        return replay

    existing_scan = db.scalar(select(Scan).where(Scan.scan_id == normalized_run_id))
    if existing_scan is not None:
        # A concurrent identical request may have committed between the first
        # idempotency lookup and this scan lookup. Restart the read snapshot so
        # the durable request binding becomes visible before declaring conflict.
        db.rollback()
        replay = _existing_result(
            db, tenant_id=tenant.tenant_id, client_request_id=request_id, payload_hash=payload_hash
        )
        if replay is not None:
            return replay
        raise ScanStartConflictError("scan_id already exists and is not bound to this client request.")

    now = _now()
    request = ScanStartRequest(
        tenant_id=tenant.tenant_id,
        client_request_id=request_id,
        payload_hash=payload_hash,
        scan_id=normalized_run_id,
        requested_scan_mode=requested_mode,
        free_scan_slot="data_health_score" if requested_mode == "data_health_score" else None,
        status="accepting",
        created_at_utc=now,
        updated_at_utc=now,
    )
    db.add(request)
    try:
        db.flush()
        product_code, credit = _resolve_access_and_credit(
            db, tenant=tenant, requested_mode=requested_mode, scan_id=normalized_run_id
        )
        request.resolved_product_code = product_code
        request.credit_id = credit.id if credit is not None else None
        request.status = "accepted"

        stored_scan_type = "data_health_score" if requested_mode == "data_health_score" else "deep"
        db.add(
            Scan(
                scan_id=normalized_run_id,
                tenant_id=tenant.tenant_id,
                scan_type=stored_scan_type,
                generated_at_utc=now,
                data_score=0,
                checks_count=0,
                issues_count=0,
                premium_available=requested_mode != "data_health_score",
                summary_headline="Data Health Score queued" if requested_mode == "data_health_score" else "Deep scan queued",
                summary_rating="Pending",
                enabled_modules=None,
            )
        )
        create_or_get_scan_run(
            db,
            run_id=normalized_run_id,
            tenant_id=tenant.tenant_id,
            scan_mode=requested_mode,
            company_name=company_name,
            environment_name=environment_name,
            status="queued",
            total_modules=max(int(total_modules or 0), 0),
        )
        if credit is not None:
            db.add(
                CreditLedgerEntry(
                    tenant_id=tenant.tenant_id,
                    credit_id=credit.id,
                    source_purchase_id=credit.source_purchase_id,
                    scan_start_request_id=request.id,
                    scan_id=normalized_run_id,
                    product_code=credit.product_code,
                    operation_type="SCAN_CONSUMED",
                    amount=-1,
                    balance_after=scan_credit_count(db, tenant.tenant_id),
                    reason="Credit consumed when scan start was durably accepted",
                    created_at_utc=now,
                )
            )
        tenant.last_seen_at_utc = now
        db.commit()
    except IntegrityError:
        db.rollback()
        replay = _existing_result(
            db, tenant_id=tenant.tenant_id, client_request_id=request_id, payload_hash=payload_hash
        )
        if replay is not None:
            return replay
        if requested_mode == "data_health_score":
            raise FreeScanAlreadyUsedError(
                "The one-time free Data Health Score has already been started for this tenant."
            )
        raise
    except Exception:
        db.rollback()
        raise

    return _result_from_request(db, request, replay=False)
