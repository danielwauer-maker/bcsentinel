from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models import Tenant
from app.security.token_hash import hash_api_token, verify_api_token
from app.services.admin_audit_service import log_admin_event
from app.services.dashboard_invite_service import DashboardUserPreparation, prepare_dashboard_user
from app.services.localization_service import normalize_language


class RegistrationConflictError(ValueError):
    pass


class RegistrationAuthenticationError(ValueError):
    pass


@dataclass(frozen=True)
class RegistrationIdentity:
    entra_tenant_id: str
    environment_name: str
    environment_type: str
    company_id: str
    company_name: str
    key: str


@dataclass(frozen=True)
class RegistrationUpsertResult:
    tenant_id: str
    api_token: str
    registration_status: str
    dashboard_user_id: int
    membership_id: int
    dashboard_access_count: int
    dashboard_user_created: bool
    membership_created: bool
    dashboard_user_email_changed: bool


def _required_text(value: str | None, field_name: str, max_length: int) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required.")
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} is too long.")
    return normalized


def build_registration_identity(
    *,
    entra_tenant_id: str | None,
    environment_name: str | None,
    environment_type: str | None,
    company_id: str | None,
    company_name: str | None,
) -> RegistrationIdentity:
    entra = _required_text(entra_tenant_id, "entra_tenant_id", 100).lower()
    env_name = _required_text(environment_name, "environment_name", 100)
    env_type = _required_text(environment_type, "environment_type", 20).lower()
    company_raw = _required_text(company_id, "company_id", 50).strip("{}")
    company = str(UUID(company_raw)).lower()
    display_name = _required_text(company_name, "company_name", 100)
    if env_type not in {"production", "sandbox", "onprem"}:
        raise ValueError("environment_type must be production, sandbox, or onprem.")

    canonical = "\n".join((entra, env_name.lower(), env_type, company))
    identity_key = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return RegistrationIdentity(
        entra_tenant_id=entra,
        environment_name=env_name,
        environment_type=env_type,
        company_id=company,
        company_name=display_name,
        key=identity_key,
    )


def _stable_tenant_id(identity_key: str) -> str:
    return f"ten_{identity_key[:24]}"


def _stable_api_token(identity_key: str) -> str:
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        f"bc-registration:{identity_key}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"tok_{digest}"


def _apply_mutable_fields(
    tenant: Tenant,
    *,
    identity: RegistrationIdentity,
    app_version: str,
    contact_email: str,
    preferred_language: str | None,
) -> None:
    tenant.environment_name = identity.environment_name
    tenant.bc_environment_name = identity.environment_name
    tenant.bc_environment_type = identity.environment_type
    tenant.bc_company_name = identity.company_name
    tenant.app_version = app_version
    tenant.contact_email = contact_email
    tenant.preferred_language = normalize_language(preferred_language)
    tenant.last_seen_at_utc = datetime.now(timezone.utc)


def _bind_identity(tenant: Tenant, identity: RegistrationIdentity) -> None:
    if tenant.registration_identity_key and tenant.registration_identity_key != identity.key:
        raise RegistrationConflictError("Existing tenant is already bound to another Business Central identity.")
    tenant.registration_identity_key = identity.key
    tenant.entra_tenant_id = identity.entra_tenant_id
    tenant.bc_environment_name = identity.environment_name
    tenant.bc_environment_type = identity.environment_type
    tenant.bc_company_id = identity.company_id
    tenant.bc_company_name = identity.company_name


def _authenticated_legacy_tenant(
    db: Session,
    *,
    existing_tenant_id: str | None,
    header_tenant_id: str | None,
    header_api_token: str | None,
) -> Tenant | None:
    requested = (existing_tenant_id or "").strip()
    if not requested:
        return None
    if requested != (header_tenant_id or "").strip() or not (header_api_token or "").strip():
        raise RegistrationAuthenticationError(
            "Binding an existing tenant requires matching tenant authentication headers."
        )
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == requested))
    if tenant is None:
        raise RegistrationAuthenticationError("Existing tenant was not found.")
    supplied_token = (header_api_token or "").strip()
    valid = False
    if tenant.api_token_hash:
        valid = verify_api_token(supplied_token, tenant.api_token_hash)
    elif tenant.api_token:
        valid = hmac.compare_digest(supplied_token, tenant.api_token)
    if not valid:
        raise RegistrationAuthenticationError("Existing tenant credentials were rejected.")
    return tenant


def upsert_tenant_registration(
    db: Session,
    *,
    identity: RegistrationIdentity,
    app_version: str,
    contact_email: str,
    preferred_language: str | None,
    existing_tenant_id: str | None = None,
    header_tenant_id: str | None = None,
    header_api_token: str | None = None,
) -> RegistrationUpsertResult:
    app_version_normalized = _required_text(app_version, "app_version", 30)
    stable_token = _stable_api_token(identity.key)
    status = "existing"

    tenant = db.scalar(select(Tenant).where(Tenant.registration_identity_key == identity.key))
    if tenant is None:
        tenant = _authenticated_legacy_tenant(
            db,
            existing_tenant_id=existing_tenant_id,
            header_tenant_id=header_tenant_id,
            header_api_token=header_api_token,
        )
        if tenant is not None:
            _bind_identity(tenant, identity)
            status = "bound_legacy"
        else:
            now = datetime.now(timezone.utc)
            tenant = Tenant(
                tenant_id=_stable_tenant_id(identity.key),
                api_token=None,
                api_token_hash=hash_api_token(stable_token),
                environment_name=identity.environment_name,
                app_version=app_version_normalized,
                contact_email=contact_email,
                preferred_language=normalize_language(preferred_language),
                created_at_utc=now,
                last_seen_at_utc=now,
                current_plan="free",
                license_status="trial",
            )
            _bind_identity(tenant, identity)
            db.add(tenant)
            status = "created"

    tenant.api_token = None
    tenant.api_token_hash = hash_api_token(stable_token)
    _apply_mutable_fields(
        tenant,
        identity=identity,
        app_version=app_version_normalized,
        contact_email=contact_email,
        preferred_language=preferred_language,
    )
    try:
        db.flush()
        preparation: DashboardUserPreparation = prepare_dashboard_user(
            db, tenant=tenant, email=contact_email
        )
        if preparation.membership_created:
            log_admin_event(
                db,
                admin_username=f"dashboard-user:{preparation.user.id}",
                action="dashboard_membership_created",
                target_type="tenant",
                target_id=tenant.tenant_id,
                details={"role": preparation.membership.role},
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        tenant = db.scalar(select(Tenant).where(Tenant.registration_identity_key == identity.key))
        if tenant is None:
            now = datetime.now(timezone.utc)
            tenant = Tenant(
                tenant_id=_stable_tenant_id(identity.key),
                api_token=None,
                api_token_hash=hash_api_token(stable_token),
                environment_name=identity.environment_name,
                app_version=app_version_normalized,
                contact_email=contact_email,
                preferred_language=normalize_language(preferred_language),
                created_at_utc=now,
                last_seen_at_utc=now,
                current_plan="free",
                license_status="trial",
            )
            _bind_identity(tenant, identity)
            db.add(tenant)
            db.flush()
            status = "created"
        else:
            status = "existing"
        _apply_mutable_fields(
            tenant,
            identity=identity,
            app_version=app_version_normalized,
            contact_email=contact_email,
            preferred_language=preferred_language,
        )
        tenant.api_token_hash = hash_api_token(stable_token)
        preparation = prepare_dashboard_user(db, tenant=tenant, email=contact_email)
        if preparation.membership_created:
            log_admin_event(
                db,
                admin_username=f"dashboard-user:{preparation.user.id}",
                action="dashboard_membership_created",
                target_type="tenant",
                target_id=tenant.tenant_id,
                details={"role": preparation.membership.role},
            )
        db.commit()

    return RegistrationUpsertResult(
        tenant_id=tenant.tenant_id,
        api_token=stable_token,
        registration_status=status,
        dashboard_user_id=preparation.user.id,
        membership_id=preparation.membership.id,
        dashboard_access_count=preparation.access_count,
        dashboard_user_created=preparation.created,
        membership_created=preparation.membership_created,
        dashboard_user_email_changed=preparation.email_changed,
    )
