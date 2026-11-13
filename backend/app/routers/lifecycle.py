from __future__ import annotations

import asyncio
import contextlib
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import SessionLocal
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.lifecycle_discovery_service import discover_scan_lifecycle_events
from app.services.lifecycle_email_service import upsert_lifecycle_profile
from app.services.lifecycle_worker_service import process_due_outbox_safely

router = APIRouter(tags=["lifecycle"])
_worker_task: asyncio.Task | None = None


class LifecycleProfileRequest(BaseModel):
    primary_notification_email: str
    preferred_language: Literal["de", "en"] = "en"


class LifecycleProfileResponse(BaseModel):
    tenant_id: str
    primary_notification_email: str
    preferred_language: str
    transactional_email_enabled: bool


@router.put("/tenant/lifecycle-profile", response_model=LifecycleProfileResponse)
def update_lifecycle_profile(
    payload: LifecycleProfileRequest,
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
) -> LifecycleProfileResponse:
    tenant_id, api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, tenant_id, api_token)
        try:
            profile = upsert_lifecycle_profile(
                db,
                tenant=tenant,
                email=payload.primary_notification_email,
                language=payload.preferred_language,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        db.commit()
        return LifecycleProfileResponse(
            tenant_id=tenant.tenant_id,
            primary_notification_email=profile.primary_notification_email,
            preferred_language=profile.preferred_language,
            transactional_email_enabled=profile.transactional_email_enabled,
        )


async def _worker_loop() -> None:
    while True:
        try:
            with SessionLocal() as db:
                discover_scan_lifecycle_events(db)
                process_due_outbox_safely(db, limit=50)
                db.commit()
        except asyncio.CancelledError:
            raise
        except Exception:
            # A database/provider failure must not terminate the API process.
            # Individual delivery errors are persisted on the outbox row.
            pass
        await asyncio.sleep(60)


@router.on_event("startup")
async def start_lifecycle_worker() -> None:
    global _worker_task
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_worker_loop())


@router.on_event("shutdown")
async def stop_lifecycle_worker() -> None:
    global _worker_task
    if _worker_task is None:
        return
    _worker_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await _worker_task
    _worker_task = None
