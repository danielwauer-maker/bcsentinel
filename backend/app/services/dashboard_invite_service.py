from __future__ import annotations

import secrets
import smtplib
from dataclasses import dataclass
from datetime import timedelta
from email.mime.text import MIMEText
from urllib.parse import urljoin

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import resolve_public_base_url, settings
from app.models import DashboardUser, Tenant
from app.security.token_hash import hash_api_token
from app.services.billing_service import utc_now
from app.services.email_template_service import render_email_template
from app.services.localization_service import normalize_language


@dataclass(frozen=True)
class DashboardInviteResult:
    user: DashboardUser
    mail_sent: bool
    mail_error: str | None = None


def ensure_dashboard_user_invite(db: Session, *, tenant: Tenant, email: str) -> DashboardInviteResult:
    normalized_email = (email or "").strip().lower()
    if not normalized_email:
        raise ValueError("contact_email is required.")

    existing_other_tenant = db.scalar(
        select(DashboardUser).where(
            DashboardUser.email == normalized_email,
            DashboardUser.tenant_id != tenant.tenant_id,
        )
    )
    if existing_other_tenant is not None:
        raise ValueError("contact_email already belongs to another tenant dashboard user.")

    now = utc_now()
    user = db.scalar(
        select(DashboardUser).where(
            DashboardUser.tenant_id == tenant.tenant_id,
            DashboardUser.email == normalized_email,
        )
    )
    if user is None:
        user = DashboardUser(
            tenant_id=tenant.tenant_id,
            email=normalized_email,
            status="invited",
            must_change_password=True,
            password_hash=None,
            created_at_utc=now,
            updated_at_utc=now,
            invite_mail_status="pending",
        )
        db.add(user)

    invite_token = secrets.token_urlsafe(32)
    user.invite_token_hash = hash_api_token(invite_token)
    user.invite_expires_at_utc = now + timedelta(days=7)
    user.status = "invited"
    user.updated_at_utc = now
    user.last_invited_at_utc = now
    user.invite_mail_status = "pending"
    user.invite_mail_error = None

    mail_sent, mail_error = _send_dashboard_invite_email(
        db,
        tenant=tenant,
        user=user,
        invite_token=invite_token,
    )
    user.invite_mail_status = "sent" if mail_sent else "failed"
    user.invite_mail_error = None if mail_sent else (mail_error or "invite mail delivery failed")
    user.updated_at_utc = utc_now()
    db.flush()
    return DashboardInviteResult(user=user, mail_sent=mail_sent, mail_error=user.invite_mail_error)


def _send_dashboard_invite_email(
    db: Session,
    *,
    tenant: Tenant,
    user: DashboardUser,
    invite_token: str,
) -> tuple[bool, str | None]:
    host = (settings.SMTP_HOST or "").strip()
    from_email = (settings.SMTP_FROM_EMAIL or "").strip()
    if not host or not from_email:
        return False, "SMTP not configured."

    language = normalize_language(getattr(tenant, "preferred_language", None))
    template_key = "dashboard_access_invite_de" if language == "de" else "dashboard_access_invite_en"
    subject, html_body = render_email_template(
        db,
        template_key,
        {
            "dashboard_url": _build_dashboard_invite_url(invite_token),
            "login_email": user.email,
            "tenant_id": tenant.tenant_id,
            "support_email": "support@bcsentinel.com",
        },
    )
    return _send_html_email(target_email=user.email, subject=subject, html_body=html_body)


def _build_dashboard_invite_url(invite_token: str) -> str:
    base_url = resolve_public_base_url() or "https://app.bcsentinel.com"
    return urljoin(f"{base_url}/", f"dashboard/invite?token={invite_token}")


def _send_html_email(*, target_email: str, subject: str, html_body: str) -> tuple[bool, str | None]:
    host = (settings.SMTP_HOST or "").strip()
    from_email = (settings.SMTP_FROM_EMAIL or "").strip()
    if not host or not from_email:
        return False, "SMTP not configured."

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>" if settings.SMTP_FROM_NAME else from_email
    msg["To"] = target_email

    try:
        with smtplib.SMTP(host, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            username = (settings.SMTP_USERNAME or "").strip()
            password = settings.SMTP_PASSWORD or ""
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(from_email, [target_email], msg.as_string())
        return True, None
    except Exception as exc:  # pragma: no cover - exact SMTP exceptions depend on deployment
        return False, str(exc)
