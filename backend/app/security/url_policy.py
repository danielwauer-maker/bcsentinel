from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


class UnsafeUrlError(ValueError):
    pass


def is_production_environment(environment: str | None) -> bool:
    return (environment or "").strip().lower() in {"prod", "production"}


def _is_loopback_host(hostname: str) -> bool:
    normalized = hostname.strip().lower().rstrip(".")
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def normalize_service_base_url(
    value: str | None,
    *,
    environment: str | None,
    allow_query: bool = False,
) -> str | None:
    normalized = (value or "").strip()
    if not normalized:
        return None
    if any(character.isspace() for character in normalized):
        raise UnsafeUrlError("Configured URL must not contain whitespace.")

    parsed = urlparse(normalized)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise UnsafeUrlError("Configured URL must be an absolute HTTP(S) URL.")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeUrlError("Configured URL must not contain embedded credentials.")
    if (parsed.query and not allow_query) or parsed.fragment:
        raise UnsafeUrlError("Configured URL contains a query or fragment that is not allowed here.")

    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise UnsafeUrlError("Configured URL contains an invalid port.") from exc

    if scheme == "http":
        if is_production_environment(environment) or not _is_loopback_host(parsed.hostname):
            raise UnsafeUrlError(
                "Unsafe API connection blocked. HTTPS is required for production environments."
            )

    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    authority = host if parsed_port is None else f"{host}:{parsed_port}"
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query and allow_query else ""
    return f"{scheme}://{authority}{path}{query}"


def request_uses_secure_transport(*, scheme: str, forwarded_proto: str | None, environment: str | None) -> bool:
    if not is_production_environment(environment):
        return True
    effective_scheme = (forwarded_proto or scheme or "").split(",", 1)[0].strip().lower()
    return effective_scheme == "https"
