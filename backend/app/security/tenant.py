import hmac

from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tenant
from app.security.tenant_session import (
    is_session_credential,
    parse_tenant_session_token,
    session_credential,
    unwrap_session_credential,
    verify_tenant_session_token,
)
from app.security.token_hash import hash_api_token, verify_api_token
from app.services.tenant_access_service import enforce_tenant_is_active

INVALID_TENANT_CREDENTIALS = "Invalid tenant credentials."


def require_tenant_headers(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_api_token: str | None = Header(default=None, alias="X-Api-Token"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> tuple[str, str]:
    auth_value = (authorization or "").strip()
    if auth_value:
        scheme, separator, token = auth_value.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token.strip():
            raise HTTPException(status_code=401, detail="Invalid tenant authorization header.")
        payload = parse_tenant_session_token(token.strip())
        if payload is None:
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
        token_tenant_id = str(payload.get("tenant_id") or "").strip()
        if x_tenant_id and x_tenant_id.strip() != token_tenant_id:
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
        if x_api_token:
            # Avoid ambiguous mixed authentication where a browser session and a
            # machine credential disagree about the effective principal.
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
        return token_tenant_id, session_credential(token.strip())

    if not x_tenant_id or not x_api_token:
        raise HTTPException(
            status_code=401,
            detail="Missing tenant authentication credentials.",
        )
    return x_tenant_id.strip(), x_api_token


def load_authenticated_tenant(
    db: Session,
    header_tenant_id: str,
    header_api_token: str,
) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == header_tenant_id))
    if tenant is None:
        # Do not disclose whether a tenant identifier exists.
        raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)

    migrate_legacy_token = False
    if is_session_credential(header_api_token):
        session_token = unwrap_session_credential(header_api_token)
        if not verify_tenant_session_token(session_token, tenant):
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
    elif tenant.api_token_hash:
        if not verify_api_token(header_api_token, tenant.api_token_hash):
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
    elif tenant.api_token:
        # Legacy fallback for existing tenants created before token hashing.
        if not hmac.compare_digest(tenant.api_token or "", header_api_token):
            raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)
        migrate_legacy_token = True
    else:
        raise HTTPException(status_code=403, detail=INVALID_TENANT_CREDENTIALS)

    # Tenant lifecycle is evaluated after credential authentication and before
    # product entitlements. A suspended/deactivated tenant therefore cannot use
    # otherwise valid paid entitlements or a still-valid browser session.
    enforce_tenant_is_active(db, tenant.tenant_id)

    if migrate_legacy_token:
        tenant.api_token_hash = hash_api_token(header_api_token)
        tenant.api_token = None
        db.commit()
        db.refresh(tenant)

    return tenant


def enforce_tenant_match(
    expected_tenant_id: str,
    header_tenant_id: str,
    source_name: str = "tenant_id",
) -> None:
    if expected_tenant_id != header_tenant_id:
        raise HTTPException(
            status_code=403,
            detail=f"{source_name} does not match authenticated tenant scope.",
        )
