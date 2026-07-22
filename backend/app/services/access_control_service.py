from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException

from app.core.observability import get_request_id, log_event
from app.models import Tenant
from app.services.product_license_service import build_product_access_snapshot

logger = logging.getLogger(__name__)

ACCESS_SNAPSHOT_VERSION = "p0d-v1"
ACCESS_SNAPSHOT_TTL_SECONDS = 60
TOKEN_AUDIENCE = "bcsentinel-protected-content"

CAPABILITY_PRODUCT = "product_access"
CAPABILITY_DASHBOARD = "dashboard_access"
CAPABILITY_ISSUES = "issues_access"
CAPABILITY_REPORT = "report_access"
CAPABILITY_MONITORING = "monitoring_access"
CAPABILITY_SUBSCRIPTION = "subscription_active"
CAPABILITY_SCAN_START = "scan_start_access"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.astimezone(timezone.utc).isoformat() if value is not None else None


def _parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _capability(*, granted: bool, valid_until: Any, reason: str) -> dict[str, Any]:
    return {
        "granted": bool(granted),
        "valid_from_utc": None,
        "valid_until_utc": _iso(_parse_utc(valid_until)),
        "end_inclusive": True,
        "reason_code": "active" if granted else reason,
    }


def build_authoritative_access_snapshot(db, tenant: Tenant, *, now: datetime | None = None) -> dict[str, Any]:
    server_time = (now or utc_now()).astimezone(timezone.utc)
    log_event(
        logger,
        logging.INFO,
        "access_snapshot_requested",
        "Authoritative access snapshot requested.",
        tenant_reference=tenant.tenant_id,
        company_reference=tenant.bc_company_id,
        capability="all",
        reason_code="snapshot_requested",
        snapshot_age_seconds=0,
        server_time=_iso(server_time),
        expiry=None,
        correlation_id=get_request_id(),
    )
    try:
        access = build_product_access_snapshot(db, tenant)
    except Exception:
        log_event(
            logger,
            logging.ERROR,
            "access_snapshot_failed",
            "Authoritative access snapshot failed.",
            tenant_reference=tenant.tenant_id,
            company_reference=tenant.bc_company_id,
            capability="all",
            reason_code="snapshot_build_failed",
            snapshot_age_seconds=0,
            server_time=_iso(server_time),
            expiry=None,
            correlation_id=get_request_id(),
        )
        raise
    premium_until = access.get("premium_access_until")
    monitoring_until = access.get("monitoring_access_until")
    capabilities = {
        CAPABILITY_PRODUCT: _capability(
            granted=bool(access["premium_active"]),
            valid_until=premium_until,
            reason="product_inactive",
        ),
        CAPABILITY_DASHBOARD: _capability(
            granted=bool(access["can_view_dashboard"]),
            valid_until=access.get("dashboard_access_until"),
            reason="dashboard_access_inactive",
        ),
        CAPABILITY_ISSUES: _capability(
            granted=bool(access["can_view_issue_details"] and access["can_view_issues"]),
            valid_until=access.get("issue_access_until"),
            reason="issues_access_inactive",
        ),
        CAPABILITY_REPORT: _capability(
            granted=bool(access["can_view_executive_report"] and access["can_view_reports"]),
            valid_until=access.get("report_access_until"),
            reason="report_access_inactive",
        ),
        CAPABILITY_MONITORING: _capability(
            granted=bool(access["can_use_monitoring"]),
            valid_until=monitoring_until,
            reason="monitoring_inactive",
        ),
        CAPABILITY_SUBSCRIPTION: _capability(
            granted=bool(access["monitoring_active"]),
            valid_until=monitoring_until,
            reason="subscription_inactive",
        ),
        CAPABILITY_SCAN_START: _capability(
            granted=bool(access["can_run_deep_scan"] or access["can_run_data_health_score"]),
            valid_until=monitoring_until if access["monitoring_active"] else premium_until,
            reason="scan_start_inactive",
        ),
    }
    snapshot = {
        "snapshot_version": ACCESS_SNAPSHOT_VERSION,
        "current_time_utc": _iso(server_time),
        "snapshot_expires_at_utc": _iso(server_time + timedelta(seconds=ACCESS_SNAPSHOT_TTL_SECONDS)),
        "cache_ttl_seconds": ACCESS_SNAPSHOT_TTL_SECONDS,
        "correlation_id": get_request_id(),
        "tenant_context": {
            "tenant_id": tenant.tenant_id,
            "entra_tenant_id": tenant.entra_tenant_id,
            "environment_name": tenant.bc_environment_name,
            "environment_type": tenant.bc_environment_type,
            "company_id": tenant.bc_company_id,
            "company_name": tenant.bc_company_name,
        },
        "capabilities": capabilities,
    }
    log_event(
        logger,
        logging.INFO,
        "access_snapshot_refreshed",
        "Authoritative access snapshot built.",
        tenant_reference=tenant.tenant_id,
        company_reference=tenant.bc_company_id,
        capability="all",
        reason_code="snapshot_refreshed",
        snapshot_age_seconds=0,
        server_time=snapshot["current_time_utc"],
        expiry=snapshot["snapshot_expires_at_utc"],
        correlation_id=get_request_id(),
    )
    return snapshot


def require_capability(
    db,
    tenant: Tenant,
    capability: str,
    *,
    denial_event: str = "protected_endpoint_blocked",
) -> dict[str, Any]:
    snapshot = build_authoritative_access_snapshot(db, tenant)
    decision = snapshot["capabilities"].get(capability)
    if decision is None:
        raise ValueError(f"Unknown access capability: {capability}")
    granted = bool(decision["granted"])
    log_event(
        logger,
        logging.INFO,
        "capability_granted" if granted else "capability_denied",
        "Protected capability decision evaluated.",
        tenant_reference=tenant.tenant_id,
        company_reference=tenant.bc_company_id,
        capability=capability,
        reason_code=decision["reason_code"],
        snapshot_age_seconds=0,
        server_time=snapshot["current_time_utc"],
        expiry=decision["valid_until_utc"],
        correlation_id=get_request_id(),
    )
    if not granted:
        log_event(
            logger,
            logging.WARNING,
            "protected_endpoint_blocked",
            "Protected endpoint blocked by capability policy.",
            tenant_reference=tenant.tenant_id,
            company_reference=tenant.bc_company_id,
            capability=capability,
            reason_code=decision["reason_code"],
            snapshot_age_seconds=0,
            server_time=snapshot["current_time_utc"],
            expiry=decision["valid_until_utc"],
            correlation_id=get_request_id(),
        )
        if denial_event != "protected_endpoint_blocked":
            log_event(
                logger,
                logging.WARNING,
                denial_event,
                "Protected token issuance denied by capability policy.",
                tenant_reference=tenant.tenant_id,
                company_reference=tenant.bc_company_id,
                capability=capability,
                reason_code=decision["reason_code"],
                snapshot_age_seconds=0,
                server_time=snapshot["current_time_utc"],
                expiry=decision["valid_until_utc"],
                correlation_id=get_request_id(),
            )
        raise HTTPException(status_code=403, detail="The requested product capability is not active.")
    return snapshot
