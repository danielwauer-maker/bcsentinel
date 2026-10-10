from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import SessionLocal
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.security.tenant_session import (
    TENANT_SESSION_MINUTES,
    TENANT_SESSION_ROLE,
    TENANT_SESSION_SCOPE,
    create_tenant_session_token,
    is_session_credential,
)
from app.services.tenant_access_service import get_tenant_status

router = APIRouter(tags=["auth"])


class TenantSessionResponse(BaseModel):
    tenant_id: str
    session_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int
    scope: str
    role: str
    tenant_status: str


@router.post("/auth/session", response_model=TenantSessionResponse)
def create_dashboard_session(
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> TenantSessionResponse:
    tenant_id, credential = tenant_auth
    if is_session_credential(credential):
        raise HTTPException(
            status_code=403,
            detail="Dashboard sessions cannot mint replacement sessions.",
        )

    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, tenant_id, credential)
        token = create_tenant_session_token(tenant)
        return TenantSessionResponse(
            tenant_id=tenant.tenant_id,
            session_token=token,
            expires_in_seconds=TENANT_SESSION_MINUTES * 60,
            scope=TENANT_SESSION_SCOPE,
            role=TENANT_SESSION_ROLE,
            tenant_status=get_tenant_status(db, tenant.tenant_id),
        )
