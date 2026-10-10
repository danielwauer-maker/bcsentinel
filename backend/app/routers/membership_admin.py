from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.account_models import TenantMembership, UserIdentity
from app.db import SessionLocal
from app.routers.account_auth import _bearer_value, _load_account_principal
from app.security.account_session import parse_user_tenant_session_token, verify_user_tenant_session_payload
from app.services.tenant_membership_admin_service import (
    accept_invitation,
    change_member_role,
    create_invitation,
    list_members,
    revoke_invitation,
    revoke_member,
)

router = APIRouter(tags=["tenant-membership-admin"])


class InviteRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    role: str = "VIEWER"


class InviteResponse(BaseModel):
    invitation_id: int
    tenant_id: str
    email: str
    role: str
    expires_at_utc: datetime
    invitation_token: str
    delivery_mode: str = "manual_until_email_integration"


class AcceptInviteRequest(BaseModel):
    invitation_token: str = Field(min_length=20, max_length=512)


class MemberRoleRequest(BaseModel):
    role: str


def _tenant_user_principal(authorization: str | None) -> tuple[int, str, str]:
    token = _bearer_value(authorization)
    payload = parse_user_tenant_session_token(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="A tenant user session is required.")
    with SessionLocal() as db:
        membership = db.get(TenantMembership, int(payload["membership_id"]))
        if membership is None or not verify_user_tenant_session_payload(payload, membership):
            raise HTTPException(status_code=403, detail="Tenant session is no longer valid.")
        return membership.user_identity_id, membership.tenant_id, membership.role


@router.post("/account/tenant/invitations", response_model=InviteResponse)
def invite_tenant_member(
    payload: InviteRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> InviteResponse:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        try:
            invitation, raw_token = create_invitation(
                db,
                tenant_id=tenant_id,
                email=payload.email,
                role=payload.role,
                actor_user_identity_id=user_id,
            )
            db.commit()
            return InviteResponse(
                invitation_id=invitation.id,
                tenant_id=invitation.tenant_id,
                email=invitation.email_normalized,
                role=invitation.role,
                expires_at_utc=invitation.expires_at_utc,
                invitation_token=raw_token,
            )
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/account/invitations/accept")
def accept_tenant_invitation(
    payload: AcceptInviteRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    with SessionLocal() as db:
        user, _ = _load_account_principal(db, authorization)
        membership = accept_invitation(db, raw_token=payload.invitation_token, user=user)
        db.commit()
        return {"status": "accepted", "tenant_id": membership.tenant_id, "role": membership.role}


@router.get("/account/tenant/members")
def get_tenant_members(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        return {"tenant_id": tenant_id, "members": list_members(db, tenant_id=tenant_id, actor_user_identity_id=user_id)}


@router.post("/account/tenant/members/{membership_id}/role")
def update_tenant_member_role(
    membership_id: int,
    payload: MemberRoleRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        try:
            membership = change_member_role(
                db,
                tenant_id=tenant_id,
                membership_id=membership_id,
                role=payload.role,
                actor_user_identity_id=user_id,
            )
            db.commit()
            return {"status": "updated", "membership_id": membership.id, "role": membership.role}
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/account/tenant/members/{membership_id}")
def remove_tenant_member(
    membership_id: int,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, tenant_id, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        try:
            membership = revoke_member(
                db,
                tenant_id=tenant_id,
                membership_id=membership_id,
                actor_user_identity_id=user_id,
            )
            db.commit()
            return {"status": "revoked", "membership_id": membership.id}
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/account/tenant/invitations/{invitation_id}")
def cancel_tenant_invitation(
    invitation_id: int,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict:
    user_id, _, _ = _tenant_user_principal(authorization)
    with SessionLocal() as db:
        try:
            invitation = revoke_invitation(db, invitation_id=invitation_id, actor_user_identity_id=user_id)
            db.commit()
            return {"status": "revoked", "invitation_id": invitation.id}
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
