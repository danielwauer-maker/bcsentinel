from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.db import SessionLocal
from app.models import CheckDefinition
from app.security.tenant import load_authenticated_tenant, require_tenant_headers
from app.services.check_catalog_service import canonicalize_language_code, resolve_check_texts


router = APIRouter(prefix="/catalog", tags=["check-catalog"])


@router.get("/checks")
def list_check_catalog(
    language: str | None = Query(default=None),
    tenant_auth: tuple[str, str] = Depends(require_tenant_headers),
):
    tenant_id, api_token = tenant_auth
    with SessionLocal() as db:
        tenant = load_authenticated_tenant(db, tenant_id, api_token)
        requested_language = canonicalize_language_code(language or tenant.preferred_language)
        fallback_order = list(dict.fromkeys((requested_language, "de-DE", "en-US", "check_id")))
        checks = db.scalars(select(CheckDefinition).order_by(CheckDefinition.check_id.asc())).all()
        texts = resolve_check_texts(db, [check.check_id for check in checks], requested_language)
        return {
            "requested_language": requested_language,
            "fallback_order": fallback_order,
            "checks": [
                {
                    "check_id": check.check_id,
                    "module": check.module,
                    "severity": check.severity,
                    "resolved_language": text.language_code,
                    "title": text.title,
                    "short_description": text.short_description,
                    "recommendation": text.recommendation,
                }
                for check in checks
                for text in [texts[check.check_id]]
            ],
        }
