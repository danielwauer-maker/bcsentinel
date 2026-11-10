from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import List, Literal, Optional
import hashlib
import json
from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import Scan, ScanExecutionEvidence, ScanExpectationSnapshot, ScanIssueRecord, ScanRunStatus, ScanStartRequest
from app.security.tenant import (
    enforce_tenant_match,
    load_authenticated_tenant,
    require_tenant_headers,
)
from app.services.finding_identity_service import resolve_finding_ids
from app.services.impact_service import (
    apply_commercials_to_scan,
    calculate_scan_commercials,
    normalize_stored_commercials,
)
from app.services.entitlement_guard_service import get_tenant_features, require_tenant_feature
from app.services.entitlement_service import is_premium_actions_enabled
from app.services.localization_service import update_tenant_language
from app.services.atomic_scan_start_service import (
    FreeScanAlreadyUsedError,
    MonitoringInactiveError,
    ScanCreditUnavailableError,
    ScanStartConflictError,
    accept_scan_start,
)
from app.services.check_catalog_service import resolve_check_texts
from app.services.scan_status_service import (
    InvalidScanTransitionError,
    ScanLeaseConflictError,
    ScanResultIncompleteError,
    create_or_get_scan_run,
    mark_scan_result_persisted,
    mark_stalled_scans,
    normalize_execution_identity,
    serialize_scan_status,
    update_scan_progress,
)

router = APIRouter(tags=["scans"])
logger = logging.getLogger(__name__)


class DataProfilePayload(BaseModel):
    customers: int = 0
    vendors: int = 0
    items: int = 0
    customer_ledger_entries: int = 0
    vendor_ledger_entries: int = 0
    item_ledger_entries: int = 0
    sales_headers: int = 0
    sales_lines: int = 0
    purchase_headers: int = 0
    purchase_lines: int = 0
    gl_entries: int = 0
    value_entries: int = 0
    warehouse_entries: int = 0
    total_records: int = 0


class ScanIssuePayload(BaseModel):
    finding_id: Optional[UUID] = None
    code: str
    category: Optional[str] = None
    title: str
    severity: str
    affected_count: int
    premium_only: bool = False
    recommendation_preview: Optional[str] = None
    estimated_impact_eur: float = 0.0


class ModuleScoresPayload(BaseModel):
    system: int = 100
    finance: int = 100
    sales: int = 100
    purchasing: int = 100
    inventory: int = 100
    crm: int = 100
    manufacturing: int = 100
    service: int = 100
    jobs: int = 100
    hr: int = 100


class CheckExecutionObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=1, max_length=50, pattern=r"^[A-Z0-9_]+$")
    status: Literal["PASS", "FINDINGS", "SKIPPED"]
    finding_count: int = Field(ge=0, le=100000)
    observed_at_utc: datetime

    @model_validator(mode="after")
    def validate_observation(self):
        if self.observed_at_utc.utcoffset() != timedelta(0):
            raise PydanticCustomError("evidence_timezone", "observed_at_utc must be UTC")
        if (self.status == "FINDINGS") != (self.finding_count > 0):
            raise PydanticCustomError("evidence_count", "finding count does not match status")
        return self


class PartialCheckExecutionEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["bc-check-execution-partial-v1"]
    checks: list[CheckExecutionObservation] = Field(max_length=1500)

    @model_validator(mode="after")
    def unique_codes(self):
        if len({item.code for item in self.checks}) != len(self.checks):
            raise PydanticCustomError("evidence_duplicate", "duplicate check code")
        return self


class ScanSyncPayload(BaseModel):
    tenant_id: str
    bc_company_id: Optional[str] = None
    lcy_code: Optional[str] = None
    preferred_language: Optional[str] = None
    scan_id: str
    scan_type: str
    generated_at_utc: datetime
    data_score: int
    checks_count: int
    issues_count: int
    applied_exception_count: int = Field(default=0, ge=0)
    premium_available: bool = True
    headline: str = ""
    rating: str = ""
    data_profile: DataProfilePayload = Field(default_factory=DataProfilePayload)
    estimated_loss_eur: float = 0.0
    potential_saving_eur: float = 0.0
    estimated_premium_price_monthly: float = 0.0
    roi_eur: float = 0.0
    module_scores: ModuleScoresPayload = Field(default_factory=ModuleScoresPayload)
    enabled_modules: List[str] = Field(default_factory=list)
    issues: List[ScanIssuePayload] = Field(default_factory=list)
    execution_token: Optional[str] = None
    worker_id: Optional[str] = None
    correlation_id: Optional[str] = None
    check_execution_evidence: Optional[PartialCheckExecutionEvidence] = None


def _canonical_execution_evidence(payload: ScanSyncPayload) -> tuple[str, str, str]:
    # Validate reported outcomes against the submitted findings without using
    # absence of a finding to infer that an unreported check executed.
    finding_counts: dict[str, int] = {}
    for issue in payload.issues:
        code = issue.code.strip().upper()
        finding_counts[code] = finding_counts.get(code, 0) + 1
    for check in payload.check_execution_evidence.checks:
        if finding_counts.get(check.code, 0) != check.finding_count:
            raise HTTPException(status_code=422, detail="Check evidence contradicts submitted finding rows.")
    evidence = payload.check_execution_evidence.model_dump(mode="json")
    evidence["checks"].sort(key=lambda item: item["code"])
    evidence_json = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if len(evidence_json.encode("utf-8")) > 500_000:
        raise HTTPException(status_code=413, detail="Check execution evidence is too large.")
    sync = payload.model_dump(mode="json", exclude={"execution_token", "worker_id", "correlation_id"})
    sync["check_execution_evidence"] = evidence
    sync["enabled_modules"] = sorted(sync["enabled_modules"])
    sync["issues"] = sorted(sync["issues"], key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    try:
        sync_json = json.dumps(sync, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except ValueError:
        raise HTTPException(status_code=422, detail="Scan sync contains non-finite values.") from None
    return evidence_json, hashlib.sha256(evidence_json.encode()).hexdigest(), hashlib.sha256(sync_json.encode()).hexdigest()


class ExpectedCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=1, max_length=50, pattern=r"^[A-Z0-9_]+$")
    module: str = Field(min_length=1, max_length=100, pattern=r"^[A-Z0-9_]+$")
    enabled: bool


class ScanStartExpectation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["bc-scan-expectation-v1"]
    methodology_version: str = Field(min_length=1, max_length=80)
    catalog_version: str = Field(min_length=1, max_length=80)
    company_id: str = Field(min_length=1, max_length=64)
    environment: str = Field(min_length=1, max_length=100)
    currency: str = Field(min_length=1, max_length=10)
    modules: list[str] = Field(min_length=1, max_length=100)
    checks: list[ExpectedCheck] = Field(min_length=1, max_length=1500)

    @model_validator(mode="after")
    def validate_sets(self):
        if len({check.code for check in self.checks}) != len(self.checks):
            raise PydanticCustomError("expectation_duplicate", "duplicate expected check")
        if any(not module.strip() or module != module.strip().upper() for module in self.modules) or len(set(self.modules)) != len(self.modules):
            raise PydanticCustomError("expectation_modules", "invalid or duplicate module")
        if not self.methodology_version.strip() or not self.catalog_version.strip() or not self.environment.strip():
            raise PydanticCustomError("expectation_metadata", "expectation metadata must be nonempty")
        return self


class ScanStartPayload(BaseModel):
    tenant_id: str
    preferred_language: Optional[str] = None
    run_id: str
    client_request_id: Optional[str] = None
    scan_mode: str = "deep"
    total_modules: int = 0
    company_name: Optional[str] = None
    environment_name: Optional[str] = None
    expectation: Optional[ScanStartExpectation] = None


class ScanReconcilePayload(BaseModel):
    tenant_id: str
    scan_ids: List[str] = Field(default_factory=list)


class ScanStatusUpdatePayload(BaseModel):
    tenant_id: str
    preferred_language: Optional[str] = None
    run_id: str
    scan_mode: str = "deep"
    status: str = "running"
    progress_percent: int = 0
    current_module: Optional[str] = None
    current_step: Optional[str] = None
    event_message: Optional[str] = None
    event_level: str = "info"
    total_modules: int = 0
    completed_modules: int = 0
    failed_modules: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    execution_token: Optional[str] = None
    worker_id: Optional[str] = None
    correlation_id: Optional[str] = None


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _lease_conflict_response(exc: ScanLeaseConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "code": exc.code,
            "message": str(exc),
            "message_de": exc.message_de,
            "details": {
                "retry_original_start": exc.code
                in {"scan_execution_token_stale", "scan_execution_lease_expired"}
            },
        },
    )


def _normalize_scan_type(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized in {"data_health_score", "free_data_health_score", "health_score"}:
        return "data_health_score"
    if normalized in {
        "deep",
        "premium_deep",
        "assessment",
        "validation",
        "validation_check",
        "monitoring",
        "scheduled",
        "manual",
    }:
        return "deep"
    if normalized == "quick":
        raise HTTPException(
            status_code=410,
            detail="Quick Scan results are no longer accepted. Use the complete Deep Scan flow.",
        )
    raise HTTPException(status_code=422, detail="Unsupported scan_type.")


def _is_free_data_health_score_scan(scan_mode: str) -> bool:
    return scan_mode == "data_health_score"


def _normalize_enabled_modules(values: List[str]) -> str:
    canonical_order = [
        "System",
        "Finance",
        "Sales",
        "Purchasing",
        "Inventory",
        "CRM",
        "Manufacturing",
        "Service",
        "Jobs",
        "HR",
    ]
    alias_map = {name.lower(): name for name in canonical_order}
    normalized: list[str] = []

    for value in values or []:
        key = str(value or "").strip().lower()
        canonical = alias_map.get(key)
        if canonical and canonical not in normalized:
            normalized.append(canonical)

    return ",".join(normalized)


def _normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _resolve_verified_scan_binding(
    payload: ScanSyncPayload, tenant: Tenant, existing_scan: Scan | None
) -> tuple[str | None, str | None]:
    """Resolve scan-time company/LCY without guessing from current tenant data.

    Legacy payloads are accepted without inventing historical bindings.
    A replay may not change an already bound scan's company or currency.
    """
    from app.services.scan_company_service import canonical_company_id, canonical_lcy_code

    bc_company_id = None
    lcy_code = None
    if payload.bc_company_id is not None or payload.lcy_code is not None:
        try:
            if not payload.bc_company_id or not payload.lcy_code:
                raise ValueError("Both BC company ID and LCY code must be sent together.")
            bc_company_id = canonical_company_id(payload.bc_company_id)
            lcy_code = canonical_lcy_code(payload.lcy_code)
            registered_company = str(tenant.bc_company_id or "").strip()
            if registered_company and canonical_company_id(registered_company) != bc_company_id:
                raise HTTPException(status_code=409, detail="Scan BC company differs from registered tenant company.")
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Invalid scan company/LCY binding.") from exc
    if existing_scan is not None and existing_scan.bc_company_id:
        if bc_company_id and existing_scan.bc_company_id != bc_company_id:
            raise HTTPException(status_code=409, detail="Scan is already bound to another BC company.")
        if lcy_code and existing_scan.lcy_code and existing_scan.lcy_code != lcy_code:
            raise HTTPException(status_code=409, detail="Scan is already bound to another LCY.")
    return bc_company_id, lcy_code


def _calculate_commercials(payload: ScanSyncPayload, db) -> dict[str, object]:
    commercials = calculate_scan_commercials(
        db,
        issues=payload.issues,
        total_records=_safe_int(payload.data_profile.total_records),
        supplied_estimated_loss_eur=_safe_float(payload.estimated_loss_eur),
        supplied_estimated_premium_price_monthly=_safe_float(payload.estimated_premium_price_monthly),
    )

    return {
        "total_records": int(commercials["total_records"]),
        "estimated_loss_eur": float(commercials["estimated_loss_eur"]),
        "potential_saving_eur": float(commercials["potential_saving_eur"]),
        "estimated_premium_price_monthly": float(commercials["estimated_premium_price_monthly"]),
        "roi_eur": float(commercials["roi_eur"]),
        "issues": list(commercials["issues"]),
    }


@router.post("/scan/start")
def start_scan(
    payload: ScanStartPayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        update_tenant_language(tenant, payload.preferred_language)
        require_tenant_feature(db, tenant, "scan_sync")
        expectation_json = None
        expectation_company = None
        if payload.expectation is not None:
            from app.services.scan_company_service import canonical_company_id, canonical_lcy_code
            from app.services.scan_comparability_service import catalog_fingerprint
            from app.services.scan_catalog_contract import CHECK_MODULE_TO_RUN_MODULE, catalog_1_0_2_57
            catalog_version, methodology_version, catalog = catalog_1_0_2_57()
            declared_pairs = frozenset((check.code, check.module) for check in payload.expectation.checks)
            if (payload.expectation.catalog_version != catalog_version
                    or payload.expectation.methodology_version != methodology_version
                    or declared_pairs != catalog):
                raise HTTPException(status_code=422, detail="Unsupported or incomplete scan check catalog.")
            modules = set(payload.expectation.modules)
            if (len(modules) != payload.total_modules
                    or not modules.issubset(set(CHECK_MODULE_TO_RUN_MODULE.values()))
                    or any(check.enabled and CHECK_MODULE_TO_RUN_MODULE[check.module] not in modules
                           for check in payload.expectation.checks)):
                raise HTTPException(status_code=422, detail="Enabled checks conflict with selected scan modules.")
            try:
                expectation_company = canonical_company_id(payload.expectation.company_id)
                if canonical_company_id(tenant.bc_company_id) != expectation_company:
                    raise ValueError("company mismatch")
                currency = canonical_lcy_code(payload.expectation.currency)
            except (ValueError, TypeError):
                raise HTTPException(status_code=409, detail="Scan expectation requires the registered company and a valid currency.") from None
            if payload.expectation.environment.strip() != (tenant.environment_name or "").strip():
                raise HTTPException(status_code=409, detail="Scan expectation environment differs from registered tenant.")
            if (payload.environment_name or "").strip() != payload.expectation.environment.strip():
                raise HTTPException(status_code=409, detail="Scan expectation environment differs from scan start.")
            expected = payload.expectation.model_dump(mode="json")
            expected["company_id"] = expectation_company
            expected["currency"] = currency
            expected["environment"] = payload.expectation.environment.strip()
            expected["modules"] = sorted(expected["modules"])
            expected["checks"] = sorted(expected["checks"], key=lambda check: check["code"])
            expected["tenant_id"] = tenant.tenant_id
            expected["scan_id"] = payload.run_id
            expected["catalog_fingerprint"] = catalog_fingerprint(
                expected["catalog_version"], expected["methodology_version"],
                tuple((check["code"], check["module"]) for check in expected["checks"]),
            )
            expectation_json = json.dumps(expected, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            if len(expectation_json.encode("utf-8")) > 500_000:
                raise HTTPException(status_code=413, detail="Scan expectation is too large.")
        request_id = payload.client_request_id or str(
            uuid5(NAMESPACE_URL, f"bcsentinel-legacy-start:{payload.tenant_id}:{payload.run_id}")
        )
        try:
            result = accept_scan_start(
                db,
                tenant=tenant,
                client_request_id=request_id,
                run_id=payload.run_id,
                scan_mode=payload.scan_mode,
                total_modules=payload.total_modules,
                company_name=payload.company_name,
                environment_name=payload.environment_name,
                expectation_json=expectation_json,
                expectation_company=expectation_company,
            )
        except ScanStartConflictError as exc:
            return JSONResponse(
                status_code=409,
                content={
                    "code": exc.code,
                    "message": str(exc),
                    "message_de": exc.message_de,
                    "details": {"retry_same_request": exc.code == "SCAN_REQUEST_PAYLOAD_CONFLICT"},
                },
            )
        except FreeScanAlreadyUsedError as exc:
            return JSONResponse(
                status_code=409,
                content={
                    "code": "FREE_SCAN_ALREADY_USED",
                    "message": str(exc),
                    "message_de": "Der einmalige kostenlose Data Health Score wurde für diesen Mandanten bereits gestartet.",
                    "details": {"retry_same_request": False},
                },
            )
        except (ScanCreditUnavailableError, MonitoringInactiveError) as exc:
            raise HTTPException(status_code=402, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except IntegrityError as exc:
            logger.exception("Atomic scan start failed because of a database conflict.")
            raise HTTPException(status_code=503, detail="The scan could not be accepted due to a temporary database conflict. Retry with the same client_request_id.") from exc

    logger.info(
        "Deep scan start accepted.",
        extra={"event": "scan_start_accepted", "tenant_id": payload.tenant_id, "scan_id": payload.run_id},
    )
    return JSONResponse(
        content={
            "status": "queued",
            "scan_id": payload.run_id,
            "scan_mode": result.scan_mode,
            "product_code": result.product_code,
            "credit_consumed": result.credit_consumed,
            "free_data_health_score": result.scan_mode == "data_health_score",
            "idempotent_replay": result.idempotent_replay,
            "execution_token": result.execution_token,
            "worker_id": result.worker_id,
            "correlation_id": result.correlation_id,
        }
    )


@router.post("/scan/sync")
def sync_scan(
    payload: ScanSyncPayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        update_tenant_language(tenant, payload.preferred_language)
        tenant_features = get_tenant_features(db, tenant)
        require_tenant_feature(db, tenant, "scan_sync")
        commercials = _calculate_commercials(payload, db)
        recalculated_issues = commercials["issues"]
        for issue, finding_id in zip(recalculated_issues, resolve_finding_ids(payload.issues)):
            issue["finding_id"] = finding_id

        existing_scan = db.scalar(select(Scan).where(Scan.scan_id == payload.scan_id).with_for_update())

        if existing_scan is not None and existing_scan.tenant_id != payload.tenant_id:
            raise HTTPException(status_code=409, detail="scan_id already exists for another tenant.")

        bc_company_id, lcy_code = _resolve_verified_scan_binding(payload, tenant, existing_scan)

        expectation = db.get(ScanExpectationSnapshot, payload.scan_id)
        if expectation is not None:
            if (expectation.tenant_id != tenant.tenant_id or expectation.company_id != bc_company_id
                    or hashlib.sha256(expectation.payload_json.encode("utf-8")).hexdigest() != expectation.payload_sha256):
                raise HTTPException(status_code=409, detail="Scan expectation binding or integrity check failed.")
            try:
                frozen = json.loads(expectation.payload_json)
                submitted_modules = sorted(name.strip().upper() for name in payload.enabled_modules)
                if (frozen["scan_id"] != payload.scan_id or frozen["tenant_id"] != tenant.tenant_id
                        or frozen["company_id"] != bc_company_id or frozen["currency"] != lcy_code
                        or frozen["environment"] != (tenant.environment_name or "").strip()
                        or frozen["modules"] != submitted_modules):
                    raise ValueError("binding or scope mismatch")
                if payload.check_execution_evidence is None:
                    raise ValueError("missing execution evidence")
                expected_checks = {item["code"]: item["enabled"] for item in frozen["checks"]}
                observations = {item.code: item for item in payload.check_execution_evidence.checks}
                accepted_at = expectation.created_at_utc
                if accepted_at.tzinfo is None:
                    accepted_at = accepted_at.replace(tzinfo=timezone.utc)
                for code, observation in observations.items():
                    if code not in expected_checks or (observation.status == "SKIPPED") == expected_checks[code]:
                        raise ValueError("check execution contradicts expectation")
                    if observation.observed_at_utc < accepted_at:
                        raise ValueError("check execution precedes accepted expectation")
                if any(issue.code.strip().upper() not in observations for issue in payload.issues):
                    raise ValueError("finding lacks an observed check")
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                raise HTTPException(status_code=409, detail="Scan sync conflicts with its start expectation.") from None

        # Partial observations are bound to an already leased scan. Never use
        # this optional payload to retrofit historical completed scans.
        evidence_values = None
        existing_evidence = db.get(ScanExecutionEvidence, payload.scan_id)
        # Legacy tenants may not have a verifiable registered company. Keep
        # their existing scan path working, but never persist the submitted
        # company claim as verified execution evidence or retrofit history.
        # The explicit response status lets clients surface the missing proof.
        evidence_unavailable_company = bool(
            existing_evidence is None and payload.check_execution_evidence is not None
            and not str(tenant.bc_company_id or "").strip()
        )
        if evidence_unavailable_company:
            payload = payload.model_copy(update={"check_execution_evidence": None})
        if existing_evidence is not None or payload.check_execution_evidence is not None:
            from app.services.scan_company_service import canonical_company_id
            if payload.check_execution_evidence is None or not bc_company_id or not lcy_code:
                raise HTTPException(status_code=409, detail="Scan execution evidence cannot be omitted or unbound.")
            try:
                if canonical_company_id(tenant.bc_company_id) != bc_company_id:
                    raise ValueError("company mismatch")
            except ValueError:
                raise HTTPException(status_code=409, detail="Scan execution evidence requires the registered company.") from None
            locked_run = db.scalar(select(ScanRunStatus).where(
                ScanRunStatus.run_id == payload.scan_id, ScanRunStatus.tenant_id == tenant.tenant_id,
            ).with_for_update())
            if (locked_run is None or not normalize_execution_identity(payload.execution_token)
                    or normalize_execution_identity(payload.execution_token) != normalize_execution_identity(locked_run.lease_token)):
                raise HTTPException(status_code=409, detail="Scan execution evidence requires its original execution lease.")
            evidence_values = _canonical_execution_evidence(payload)
            if existing_evidence is not None:
                if (existing_evidence.tenant_id != tenant.tenant_id or existing_evidence.company_id != bc_company_id
                        or existing_evidence.payload_sha256 != evidence_values[1] or existing_evidence.sync_sha256 != evidence_values[2]):
                    raise HTTPException(status_code=409, detail="Finalized scan execution evidence conflicts with this retry.")
                original_request = db.scalar(select(ScanStartRequest).where(ScanStartRequest.scan_id == payload.scan_id))
                if (locked_run.status not in {"completed", "completed_with_warnings"} or original_request is None
                        or normalize_execution_identity(original_request.client_request_id) != normalize_execution_identity(payload.worker_id)):
                    raise HTTPException(status_code=409, detail="Scan execution evidence retry does not match the original worker.")
                stored_issues = db.scalars(select(ScanIssueRecord).where(
                    ScanIssueRecord.scan_id == payload.scan_id,
                ).order_by(ScanIssueRecord.id)).all()
                return JSONResponse(content={
                    "status": "ok", "scan_id": payload.scan_id, "tenant_id": payload.tenant_id,
                    "execution_evidence_status": "partial_stored",
                    "scan_status": jsonable_encoder(serialize_scan_status(db, locked_run)),
                    "commercials": normalize_stored_commercials(
                        total_records=existing_scan.total_records,
                        estimated_loss_eur=existing_scan.estimated_loss_eur,
                        potential_saving_eur=existing_scan.potential_saving_eur,
                        estimated_premium_price_monthly=existing_scan.estimated_premium_price_monthly,
                    ),
                    "issues": [{"finding_id": issue.finding_id, "code": issue.code,
                                "category": issue.category, "title": issue.title, "severity": issue.severity,
                                "affected_count": issue.affected_count, "premium_only": issue.premium_only,
                                "recommendation_preview": issue.recommendation_preview,
                                "estimated_impact_eur": issue.estimated_impact_eur} for issue in stored_issues],
                })
            elif locked_run.status in {"completed", "completed_with_warnings", "failed", "cancelled", "expired"}:
                raise HTTPException(status_code=409, detail="Historical or finalized scans cannot acquire execution evidence.")

        normalized_scan_type = _normalize_scan_type(payload.scan_type)
        if existing_scan is None and normalized_scan_type in {"deep", "data_health_score"}:
            legacy_request_id = str(
                uuid5(NAMESPACE_URL, f"bcsentinel-legacy-sync:{payload.tenant_id}:{payload.scan_id}")
            )
            try:
                accept_scan_start(
                    db,
                    tenant=tenant,
                    client_request_id=legacy_request_id,
                    run_id=payload.scan_id,
                    scan_mode=payload.scan_type,
                    total_modules=len(payload.enabled_modules or []),
                    company_name=None,
                    environment_name=None,
                )
            except (ScanCreditUnavailableError, MonitoringInactiveError) as exc:
                raise HTTPException(status_code=402, detail=str(exc)) from exc
            except (ScanStartConflictError, FreeScanAlreadyUsedError) as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            existing_scan = db.scalar(select(Scan).where(Scan.scan_id == payload.scan_id).with_for_update())

        scan = existing_scan
        scan_created_without_start = False
        normalized_generated_at = _normalize_utc(payload.generated_at_utc)
        is_free_score = _is_free_data_health_score_scan(normalized_scan_type)
        if scan is None:
            scan_created_without_start = True
            scan = Scan(
                scan_id=payload.scan_id,
                tenant_id=payload.tenant_id,
                # Technical scan type is always deep; access tier is tracked
                # independently by the scan-start entitlement/credit ledger.
                scan_type="deep",
                generated_at_utc=normalized_generated_at,
                data_score=_safe_int(payload.data_score),
                checks_count=_safe_int(payload.checks_count),
                issues_count=_safe_int(payload.issues_count),
                applied_exception_count=_safe_int(payload.applied_exception_count),
                premium_available=is_premium_actions_enabled(tenant_features),
                summary_headline=payload.headline or "",
                summary_rating=payload.rating or "",
                enabled_modules=_normalize_enabled_modules(payload.enabled_modules),
            )
            db.add(scan)
            db.flush()
            create_or_get_scan_run(
                db,
                run_id=payload.scan_id,
                tenant_id=payload.tenant_id,
                scan_mode=normalized_scan_type,
                status="preparing",
                total_modules=len(payload.enabled_modules or []),
            )
        else:
            scan.tenant_id = payload.tenant_id
            scan.scan_type = "deep"
            scan.generated_at_utc = normalized_generated_at
            scan.data_score = _safe_int(payload.data_score)
            scan.checks_count = _safe_int(payload.checks_count)
            scan.issues_count = _safe_int(payload.issues_count)
            scan.applied_exception_count = _safe_int(payload.applied_exception_count)
            scan.premium_available = is_premium_actions_enabled(tenant_features)
            scan.summary_headline = payload.headline or ""
            scan.summary_rating = payload.rating or ""
            scan.enabled_modules = _normalize_enabled_modules(payload.enabled_modules)



        if bc_company_id:
            scan.bc_company_id = bc_company_id
            scan.lcy_code = lcy_code

        apply_commercials_to_scan(scan, commercials)

        scan.system_score = _safe_int(payload.module_scores.system)
        scan.finance_score = _safe_int(payload.module_scores.finance)
        scan.sales_score = _safe_int(payload.module_scores.sales)
        scan.purchasing_score = _safe_int(payload.module_scores.purchasing)
        scan.inventory_score = _safe_int(payload.module_scores.inventory)
        scan.crm_score = _safe_int(payload.module_scores.crm)
        scan.manufacturing_score = _safe_int(payload.module_scores.manufacturing)
        scan.service_score = _safe_int(payload.module_scores.service)
        scan.jobs_score = _safe_int(payload.module_scores.jobs)
        scan.hr_score = _safe_int(payload.module_scores.hr)

        scan.customers_count = _safe_int(payload.data_profile.customers)
        scan.vendors_count = _safe_int(payload.data_profile.vendors)
        scan.items_count = _safe_int(payload.data_profile.items)
        scan.customer_ledger_entries_count = _safe_int(payload.data_profile.customer_ledger_entries)
        scan.vendor_ledger_entries_count = _safe_int(payload.data_profile.vendor_ledger_entries)
        scan.item_ledger_entries_count = _safe_int(payload.data_profile.item_ledger_entries)
        scan.sales_headers_count = _safe_int(payload.data_profile.sales_headers)
        scan.sales_lines_count = _safe_int(payload.data_profile.sales_lines)
        scan.purchase_headers_count = _safe_int(payload.data_profile.purchase_headers)
        scan.purchase_lines_count = _safe_int(payload.data_profile.purchase_lines)
        scan.gl_entries_count = _safe_int(payload.data_profile.gl_entries)
        scan.value_entries_count = _safe_int(payload.data_profile.value_entries)
        scan.warehouse_entries_count = _safe_int(payload.data_profile.warehouse_entries)

        tenant.last_seen_at_utc = datetime.now(timezone.utc)
        catalog_texts = resolve_check_texts(
            db,
            {str(issue["code"]) for issue in recalculated_issues},
            tenant.preferred_language,
        )
        existing_issues = {issue.finding_id: issue for issue in db.scalars(
            select(ScanIssueRecord).where(ScanIssueRecord.scan_id == payload.scan_id)
        )}
        incoming_ids = set()
        for issue in recalculated_issues:
            finding_id = str(issue["finding_id"])
            incoming_ids.add(finding_id)
            stored = existing_issues.get(finding_id)
            if stored is not None and stored.code != str(issue["code"]):
                raise HTTPException(status_code=409, detail="Finding identity cannot change check within a scan.")
            if stored is None:
                stored = ScanIssueRecord(scan_id=payload.scan_id, finding_id=finding_id, code=str(issue["code"]))
                db.add(stored)
            catalog_text = catalog_texts[str(issue["code"])]
            stored.category = (str(issue.get("category")).strip() or None) if issue.get("category") is not None else None
            stored.title = catalog_text.title
            stored.severity = str(issue["severity"])
            stored.affected_count = _safe_int(issue["affected_count"])
            stored.premium_only = bool(issue["premium_only"])
            stored.recommendation_preview = catalog_text.recommendation
            stored.estimated_impact_eur = _safe_float(issue["estimated_impact_eur"])
        # Sync is an atomic complete snapshot, as before; other scans are untouched.
        for finding_id, stored in existing_issues.items():
            if finding_id not in incoming_ids:
                db.delete(stored)

        db.flush()
        run = db.scalar(select(ScanRunStatus).where(ScanRunStatus.run_id == payload.scan_id))
        if run is None:
            raise HTTPException(status_code=409, detail="The scan lifecycle record is missing.")
        request = db.scalar(select(ScanStartRequest).where(ScanStartRequest.scan_id == payload.scan_id))
        legacy_request_id = str(uuid5(NAMESPACE_URL, f"bcsentinel-legacy-sync:{payload.tenant_id}:{payload.scan_id}"))
        legacy_unleased = bool(request and request.client_request_id == legacy_request_id and not payload.execution_token)
        if request is not None and not payload.execution_token and not legacy_unleased:
            raise HTTPException(status_code=409, detail="The scan execution token is required. Refresh the original scan start and retry the same run.")
        try:
            if legacy_unleased and run.status in {"queued", "preparing"}:
                update_scan_progress(
                    db,
                    run_id=payload.scan_id,
                    tenant_id=payload.tenant_id,
                    scan_mode=normalized_scan_type,
                    status="running",
                    progress_percent=99,
                    current_module="Legacy sync",
                    current_step="Persisting scan result",
                    event_message="Legacy scan result received",
                    allow_unleased=True,
                )
            elif payload.execution_token and run.status in {"queued", "preparing"}:
                update_scan_progress(
                    db,
                    run_id=payload.scan_id,
                    tenant_id=payload.tenant_id,
                    scan_mode=normalized_scan_type,
                    status="running",
                    progress_percent=99,
                    current_module="Finalizing",
                    current_step="Persisting scan result",
                    event_message="Final scan result received",
                    lease_token=payload.execution_token,
                    worker_id=payload.worker_id,
                    correlation_id=payload.correlation_id,
                )
            mark_scan_result_persisted(db, run)
            update_scan_progress(
                db,
                run_id=payload.scan_id,
                tenant_id=payload.tenant_id,
                scan_mode=normalized_scan_type,
                status="completed",
                progress_percent=100,
                current_module="Finalizing",
                current_step="Scan synchronized",
                event_message="Scan completed",
                total_modules=len(payload.enabled_modules or []),
                completed_modules=len(payload.enabled_modules or []),
                lease_token=payload.execution_token,
                worker_id=payload.worker_id,
                correlation_id=payload.correlation_id,
                allow_unleased=legacy_unleased or request is None,
                result_is_persisted=True,
            )
        except ScanLeaseConflictError as exc:
            logger.warning(
                "Late or unowned scan result rejected.",
                extra={
                    "event": "late_worker_result_rejected",
                    "scan_id": payload.scan_id,
                    "tenant_id": payload.tenant_id,
                    "worker_id": payload.worker_id,
                    "correlation_id": payload.correlation_id,
                },
            )
            return _lease_conflict_response(exc)
        except (InvalidScanTransitionError, ScanResultIncompleteError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        # v2: persist the observed (NOT customer-confirmed) module scope in
        # the same transaction as the finalized scan. No background retry,
        # synthetic baseline, or new scan is required for report preflight.
        from app.core.settings import settings
        if settings.ACCESS_MODEL_V2_ENABLED:
            from app.services.assessment_scope_service import get_or_create_auto_scope
            get_or_create_auto_scope(db, scan, commit=False)

        if evidence_values is not None and existing_evidence is None:
            db.add(ScanExecutionEvidence(
                scan_id=scan.scan_id, tenant_id=tenant.tenant_id, company_id=bc_company_id,
                schema_version=payload.check_execution_evidence.schema_version,
                payload_json=evidence_values[0], payload_sha256=evidence_values[1], sync_sha256=evidence_values[2],
                created_at_utc=datetime.now(timezone.utc),
            ))
            db.flush()

        scan_status = serialize_scan_status(db, run)
        db.commit()

    logger.info(
        "Scan sync completed.",
        extra={
            "event": "scan_sync_completed",
            "tenant_id": payload.tenant_id,
            "scan_id": payload.scan_id,
            "scan_type": normalized_scan_type,
        },
    )

    return JSONResponse(
        content={
            "status": "ok",
            "scan_id": payload.scan_id,
            "tenant_id": payload.tenant_id,
            "scan_status": jsonable_encoder(scan_status),
            "execution_evidence_status": "unavailable_company_binding" if evidence_unavailable_company else (
                "partial_stored" if evidence_values is not None else "not_supplied"
            ),
            "commercials": normalize_stored_commercials(
                total_records=int(commercials["total_records"]),
                estimated_loss_eur=float(commercials["estimated_loss_eur"]),
                potential_saving_eur=float(commercials["potential_saving_eur"]),
                estimated_premium_price_monthly=float(commercials["estimated_premium_price_monthly"]),
            ),
            "issues": recalculated_issues,
        }
    )


@router.post("/scan/reconcile")
def reconcile_scans(
    payload: ScanReconcilePayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")

    keep_ids = {scan_id.strip() for scan_id in payload.scan_ids if scan_id and scan_id.strip()}

    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)

        scans = db.scalars(select(Scan).where(Scan.tenant_id == payload.tenant_id)).all()
        deleted_ids: list[str] = []

        for scan in scans:
            if scan.scan_id not in keep_ids:
                deleted_ids.append(scan.scan_id)
                db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == scan.scan_id).delete()
                db.delete(scan)

        db.commit()

    logger.info(
        "Scan reconcile completed.",
        extra={
            "event": "scan_reconcile_completed",
            "tenant_id": payload.tenant_id,
            "deleted_count": len(deleted_ids),
            "kept_count": len(keep_ids),
        },
    )

    return JSONResponse(
        content={
            "status": "ok",
            "tenant_id": payload.tenant_id,
            "deleted_scan_ids": deleted_ids,
            "kept_scan_ids": sorted(keep_ids),
        }
    )


@router.delete("/scan/{tenant_id}/{scan_id}")
def delete_scan(
    tenant_id: str,
    scan_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(tenant_id, header_tenant_id, "Path tenant_id")

    with SessionLocal() as db:
        load_authenticated_tenant(db, header_tenant_id, header_api_token)
        scan = db.scalar(select(Scan).where(Scan.tenant_id == tenant_id, Scan.scan_id == scan_id))

        if scan is None:
            return JSONResponse(content={"status": "not_found", "scan_id": scan_id})

        db.query(ScanIssueRecord).filter(ScanIssueRecord.scan_id == scan_id).delete()
        db.delete(scan)
        db.commit()

    logger.info(
        "Scan deleted.",
        extra={"event": "scan_deleted", "tenant_id": tenant_id, "scan_id": scan_id},
    )

    return JSONResponse(content={"status": "deleted", "scan_id": scan_id})


@router.post("/scan/status/update")
def update_status(
    payload: ScanStatusUpdatePayload,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth
    enforce_tenant_match(payload.tenant_id, header_tenant_id, "Payload tenant_id")

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        require_tenant_feature(db, tenant, "scan_sync")
        try:
            run = update_scan_progress(
                db,
                run_id=payload.run_id,
                tenant_id=payload.tenant_id,
                scan_mode=payload.scan_mode,
                status=payload.status,
                progress_percent=payload.progress_percent,
                current_module=payload.current_module,
                current_step=payload.current_step,
                event_message=payload.event_message,
                event_level=payload.event_level,
                total_modules=payload.total_modules,
                completed_modules=payload.completed_modules,
                failed_modules=payload.failed_modules,
                error_code=payload.error_code,
                error_message=payload.error_message,
                warning_message=payload.warning_message,
                lease_token=payload.execution_token,
                worker_id=payload.worker_id,
                correlation_id=payload.correlation_id,
            )
        except ScanLeaseConflictError as exc:
            logger.warning(
                "Scan update rejected because the worker lease is not current.",
                extra={
                    "event": "late_worker_result_rejected",
                    "scan_id": payload.run_id,
                    "tenant_id": payload.tenant_id,
                    "worker_id": payload.worker_id,
                    "correlation_id": payload.correlation_id,
                },
            )
            return _lease_conflict_response(exc)
        except (InvalidScanTransitionError, ScanResultIncompleteError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        db.commit()
        return JSONResponse(content=jsonable_encoder(serialize_scan_status(db, run, include_execution_token=True)))


@router.get("/scan/status/latest")
def get_latest_scan_status(
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        require_tenant_feature(db, tenant, "scan_sync")
        mark_stalled_scans(db)
        run = db.scalar(
            select(ScanRunStatus)
            .where(ScanRunStatus.tenant_id == tenant.tenant_id)
            .order_by(ScanRunStatus.updated_at_utc.desc(), ScanRunStatus.id.desc())
        )
        db.commit()

        if run is None:
            raise HTTPException(status_code=404, detail="No scan status found.")

        return JSONResponse(content=jsonable_encoder(serialize_scan_status(db, run)))


@router.get("/scan/status/{run_id}")
def get_scan_status(
    run_id: str,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    header_tenant_id, header_api_token = tenant_auth

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, header_tenant_id, header_api_token)
        require_tenant_feature(db, tenant, "scan_sync")
        mark_stalled_scans(db)
        run = db.scalar(
            select(ScanRunStatus).where(
                ScanRunStatus.run_id == run_id,
                ScanRunStatus.tenant_id == tenant.tenant_id,
            )
        )
        db.commit()

        if run is None:
            raise HTTPException(status_code=404, detail="Scan status not found.")

        return JSONResponse(content=jsonable_encoder(serialize_scan_status(db, run)))
