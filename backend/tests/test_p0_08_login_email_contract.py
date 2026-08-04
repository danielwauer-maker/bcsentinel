from __future__ import annotations

from pathlib import Path

from app.routers import dashboard
from app.services import dashboard_invite_service


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_SOURCE = ROOT / "backend/app/routers/dashboard.py"
INVITE_SOURCE = ROOT / "backend/app/services/dashboard_invite_service.py"
TEMPLATE_SERVICE = ROOT / "backend/app/services/email_template_service.py"


def _route_map(router):
    return {(route.path, method) for route in router.routes for method in getattr(route, "methods", set())}


def test_login_invite_and_logout_routes_are_present():
    routes = _route_map(dashboard.router)
    assert {
        ("/dashboard/invite/activate", "POST"),
        ("/dashboard/login", "POST"),
        ("/dashboard/logout", "POST"),
    } <= routes


def test_login_failure_is_generic_and_does_not_enumerate_users():
    source = DASHBOARD_SOURCE.read_text(encoding="utf-8")
    assert '"DASHBOARD_LOGIN_FAILED"' in source
    assert '"Email or password is invalid."' in source
    assert '"E-Mail-Adresse oder Kennwort ist ungültig."' in source
    assert "user is None or user.status != \"active\" or not verify_api_token" in source


def test_invite_activation_requires_strong_password_and_invalidates_token():
    source = DASHBOARD_SOURCE.read_text(encoding="utf-8")
    assert "if len(payload.password) < 12" in source
    assert "user.invite_token_hash = None" in source
    assert "user.invite_expires_at_utc = None" in source
    assert 'user.status = "active"' in source
    assert "expires_at <= now" in source


def test_invite_token_is_random_hashed_and_time_limited():
    source = INVITE_SOURCE.read_text(encoding="utf-8")
    assert "secrets.token_urlsafe(32)" in source
    assert "hash_api_token(invite_token)" in source
    assert "timedelta(days=7)" in source
    assert 'user.invite_mail_status = "pending"' in source
    assert '"sent" if mail_sent else "failed"' in source


def test_smtp_delivery_contract_supports_tls_auth_timeout_and_status_errors():
    source = INVITE_SOURCE.read_text(encoding="utf-8")
    assert "smtplib.SMTP(host, settings.SMTP_PORT, timeout=15)" in source
    assert "if settings.SMTP_USE_TLS" in source
    assert "smtp.starttls()" in source
    assert "smtp.login(username, password)" in source
    assert "smtp.sendmail(from_email, [target_email], msg.as_string())" in source
    assert 'return False, "SMTP not configured."' in source
    assert "return False, str(exc)" in source


def test_invite_email_uses_localized_templates_and_public_dashboard_url():
    source = INVITE_SOURCE.read_text(encoding="utf-8")
    assert '"dashboard_access_invite_de"' in source
    assert '"dashboard_access_invite_en"' in source
    assert '"dashboard_url"' in source
    assert '"login_email"' in source
    assert '"support_email"' in source
    assert "resolve_public_base_url()" in source
    assert TEMPLATE_SERVICE.exists()
