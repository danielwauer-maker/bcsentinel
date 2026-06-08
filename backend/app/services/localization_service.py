from __future__ import annotations

from app.models import Tenant

SUPPORTED_LANGUAGES = {"de", "en"}
DEFAULT_LANGUAGE = "en"


def normalize_language(value: object | None) -> str:
    normalized = str(value or "").strip().lower().replace("_", "-")
    if normalized == "de" or normalized.startswith("de-"):
        return "de"
    return DEFAULT_LANGUAGE


def tenant_language(tenant: Tenant | None) -> str:
    if tenant is None:
        return DEFAULT_LANGUAGE
    return normalize_language(getattr(tenant, "preferred_language", None))


def update_tenant_language(tenant: Tenant, value: object | None) -> bool:
    if value is None or str(value).strip() == "":
        return False
    normalized = normalize_language(value)
    if getattr(tenant, "preferred_language", None) == normalized:
        return False
    tenant.preferred_language = normalized
    return True
