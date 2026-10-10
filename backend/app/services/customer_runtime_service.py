from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.customer_runtime_models import TenantBillingProfile, TenantConnectionDiagnostic, TenantCustomerLifecycle
from app.models import AdminAuditEvent, Tenant

LIFECYCLE_STATES = {
    "invited", "onboarding", "pilot", "active", "grace_period", "payment_failed",
    "suspended", "canceled", "expired", "archived",
}
LIFECYCLE_TRANSITIONS = {
    "invited": {"onboarding", "archived"},
    "onboarding": {"pilot", "active", "canceled", "archived"},
    "pilot": {"active", "grace_period", "expired", "canceled"},
    "active": {"grace_period", "payment_failed", "suspended", "canceled"},
    "grace_period": {"active", "payment_failed", "expired", "canceled"},
    "payment_failed": {"active", "grace_period", "suspended", "canceled", "expired"},
    "suspended": {"active", "canceled", "expired"},
    "canceled": {"active", "archived"},
    "expired": {"active", "archived"},
    "archived": set(),
}
LIFECYCLE_ACCESS = {
    "invited": "none",
    "onboarding": "onboarding_only",
    "pilot": "entitlement_driven",
    "active": "entitlement_driven",
    "grace_period": "read_only_grace",
    "payment_failed": "read_only_grace",
    "suspended": "locked",
    "canceled": "read_only_retention",
    "expired": "read_only_retention",
    "archived": "none",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _audit(db, *, actor: str, action: str, tenant_id: str, details: dict) -> None:
    db.add(AdminAuditEvent(
        admin_username=actor[:120], action=action[:80], target_type="tenant", target_id=tenant_id,
        details_json=json.dumps(details, sort_keys=True, default=str), created_at_utc=utc_now(),
    ))


def get_lifecycle(db, tenant_id: str) -> TenantCustomerLifecycle:
    row = db.get(TenantCustomerLifecycle, tenant_id)
    if row is None:
        now = utc_now()
        row = TenantCustomerLifecycle(
            tenant_id=tenant_id, state="onboarding", effective_from_utc=now,
            updated_by="system", updated_at_utc=now,
        )
        db.add(row)
        db.flush()
    return row


def transition_lifecycle(db, *, tenant_id: str, new_state: str, actor: str, reason: str | None = None,
                         grace_until_utc: datetime | None = None, pilot_until_utc: datetime | None = None) -> TenantCustomerLifecycle:
    if db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id)) is None:
        raise ValueError("Tenant not found.")
    state = (new_state or "").strip().lower()
    if state not in LIFECYCLE_STATES:
        raise ValueError("Unsupported customer lifecycle state.")
    row = get_lifecycle(db, tenant_id)
    old = row.state
    if old != state and state not in LIFECYCLE_TRANSITIONS.get(old, set()):
        raise ValueError(f"Lifecycle transition {old} -> {state} is not allowed.")
    now = utc_now()
    row.state = state
    row.effective_from_utc = now
    row.grace_until_utc = grace_until_utc
    row.pilot_until_utc = pilot_until_utc
    row.reason = (reason or "").strip() or None
    row.updated_by = actor
    row.updated_at_utc = now
    _audit(db, actor=actor, action="customer_lifecycle.transition", tenant_id=tenant_id,
           details={"from": old, "to": state, "reason": reason})
    return row


def lifecycle_access_mode(row: TenantCustomerLifecycle) -> str:
    return LIFECYCLE_ACCESS[row.state]


def upsert_billing_profile(db, *, tenant_id: str, actor: str, legal_company_name: str, billing_email: str,
                           address_line1: str, postal_code: str, city: str, country_code: str,
                           address_line2: str | None = None, region: str | None = None,
                           vat_id: str | None = None) -> TenantBillingProfile:
    required = [legal_company_name, billing_email, address_line1, postal_code, city, country_code]
    if any(not str(v or "").strip() for v in required):
        raise ValueError("Required billing identity fields are missing.")
    if "@" not in billing_email:
        raise ValueError("A valid billing email is required.")
    country = country_code.strip().upper()
    if len(country) != 2 or not country.isalpha():
        raise ValueError("country_code must be ISO alpha-2.")
    now = utc_now()
    row = db.get(TenantBillingProfile, tenant_id)
    created = row is None
    if row is None:
        row = TenantBillingProfile(tenant_id=tenant_id, created_at_utc=now, updated_at_utc=now,
                                   updated_by=actor, legal_company_name="", billing_email="",
                                   address_line1="", postal_code="", city="", country_code=country)
        db.add(row)
    row.legal_company_name = legal_company_name.strip()
    row.billing_email = billing_email.strip().casefold()
    row.address_line1 = address_line1.strip()
    row.address_line2 = (address_line2 or "").strip() or None
    row.postal_code = postal_code.strip()
    row.city = city.strip()
    row.region = (region or "").strip() or None
    row.country_code = country
    row.vat_id = (vat_id or "").strip().upper() or None
    row.tax_treatment = "provider_determined"
    row.updated_by = actor
    row.updated_at_utc = now
    db.flush()
    _audit(db, actor=actor, action="billing_profile.upsert", tenant_id=tenant_id,
           details={"created": created, "country_code": country, "has_vat_id": bool(row.vat_id)})
    return row


def record_provider_tax_evidence(db, *, tenant_id: str, actor: str, provider_customer_id: str,
                                 tax_treatment: str, evidence: dict) -> TenantBillingProfile:
    row = db.get(TenantBillingProfile, tenant_id)
    if row is None:
        raise ValueError("Billing profile must exist before provider tax evidence is recorded.")
    row.provider_customer_id = provider_customer_id.strip()
    row.tax_treatment = tax_treatment.strip().lower()
    row.provider_tax_evidence_json = json.dumps(evidence, sort_keys=True, default=str)
    row.updated_by = actor
    row.updated_at_utc = utc_now()
    _audit(db, actor=actor, action="billing_profile.tax_evidence", tenant_id=tenant_id,
           details={"provider_customer_id": provider_customer_id, "tax_treatment": tax_treatment})
    return row


def _compatibility_policy() -> dict:
    path = Path(__file__).resolve().parents[3] / "config" / "bc-compatibility.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _version_tuple(value: str | None) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in str(value or "").split(".") if part != "")
    except ValueError:
        return ()


def evaluate_connection(*, extension_version: str | None, bc_version: str | None,
                        api_reachable: bool | None, permissions_ok: bool | None) -> dict:
    policy = _compatibility_policy()
    minimum = _version_tuple(policy["minimum_extension_version"])
    extension = _version_tuple(extension_version)
    bc = _version_tuple(bc_version)
    upgrade_required = bool(extension and minimum and extension < minimum)
    if api_reachable is False:
        return {"status": "blocked", "upgrade_required": upgrade_required, "code": "API_UNREACHABLE",
                "message": "Business Central API is not reachable. Check connection and authentication."}
    if permissions_ok is False:
        return {"status": "blocked", "upgrade_required": upgrade_required, "code": "PERMISSIONS_MISSING",
                "message": "Required BCSentinel permissions are missing in Business Central."}
    if not extension:
        return {"status": "unknown", "upgrade_required": False, "code": "EXTENSION_VERSION_UNKNOWN",
                "message": "BCSentinel extension version could not be determined."}
    if upgrade_required:
        return {"status": "upgrade_required", "upgrade_required": True, "code": "EXTENSION_OUTDATED",
                "message": f"BCSentinel extension {extension_version} is below the supported minimum {policy['minimum_extension_version']}."}
    if not bc:
        return {"status": "unknown", "upgrade_required": False, "code": "BC_VERSION_UNKNOWN",
                "message": "Business Central version could not be determined."}
    if bc[0] not in set(policy["supported_bc_major_versions"]):
        return {"status": "unsupported", "upgrade_required": False, "code": "BC_VERSION_UNSUPPORTED",
                "message": f"Business Central major version {bc[0]} is outside the supported compatibility policy."}
    if api_reachable is True and permissions_ok is True:
        return {"status": "compatible", "upgrade_required": False, "code": "OK",
                "message": "Business Central connection, permissions and version policy are compatible."}
    return {"status": "partial", "upgrade_required": False, "code": "CHECKS_INCOMPLETE",
            "message": "Connection diagnostics are incomplete."}


def record_connection_diagnostic(db, *, tenant_id: str, environment_name: str | None, company_name: str | None,
                                 extension_version: str | None, bc_version: str | None,
                                 api_reachable: bool | None, permissions_ok: bool | None) -> TenantConnectionDiagnostic:
    result = evaluate_connection(extension_version=extension_version, bc_version=bc_version,
                                 api_reachable=api_reachable, permissions_ok=permissions_ok)
    row = TenantConnectionDiagnostic(
        tenant_id=tenant_id, environment_name=environment_name, company_name=company_name,
        extension_version=extension_version, bc_version=bc_version,
        api_reachable="true" if api_reachable is True else "false" if api_reachable is False else "unknown",
        permissions_ok="true" if permissions_ok is True else "false" if permissions_ok is False else "unknown",
        compatibility_status=result["status"], upgrade_required="true" if result["upgrade_required"] else "false",
        diagnostic_code=result["code"], message=result["message"], observed_at_utc=utc_now(),
    )
    db.add(row)
    db.flush()
    return row
