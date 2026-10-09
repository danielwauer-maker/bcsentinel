from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "backend/app/routers/notifications.py"
MODEL = ROOT / "backend/app/notification_models.py"
LICENSE = ROOT / "backend/app/routers/license.py"
MIGRATION = ROOT / "backend/alembic/versions/0019_notification_settings_read_model.py"


def require(text: str, needle: str, source: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: missing {needle!r} in {source}")


def forbid(text: str, needle: str, source: str) -> None:
    if needle in text:
        raise SystemExit(f"FAIL: forbidden {needle!r} in {source}")


def main() -> None:
    for path in (ROUTER, MODEL, LICENSE, MIGRATION):
        if not path.exists():
            raise SystemExit(f"FAIL: missing {path.relative_to(ROOT)}")

    router = ROUTER.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    license_router = LICENSE.read_text(encoding="utf-8")
    migration = MIGRATION.read_text(encoding="utf-8")

    require(router, '@router.post("/read-model/sync")', "notifications router")
    require(router, '@router.get("/settings")', "notifications router")
    require(router, "load_authenticated_tenant", "notifications router")
    require(router, "enforce_tenant_match", "notifications router")
    require(router, '"manage_in_business_central_hint": True', "notifications router")
    require(router, '"dashboard_mode": "read_only"', "notifications router")
    require(router, "success_rate_pct", "notifications router")
    require(router, "safe_last_failure_summary", "notifications router")
    require(router, "CANONICAL_EVENT_TYPES", "notifications router")
    require(router, 'CANONICAL_CHANNELS = {"email"}', "notifications router")

    # Dashboard surface must stay read-only. The only POST is the BC-originated sync endpoint.
    for token in ('@router.put(', '@router.patch(', '@router.delete(', 'send_test_email', 'force_retry'):
        forbid(router, token, "notifications router")

    # Do not persist recipient addresses, template bodies or provider secrets in the dashboard read model.
    for token in ("email_address", "subject_template", "body_template", "provider_message_id", "smtp_password", "api_token"):
        forbid(model.lower(), token, "notification model")

    require(model, 'UniqueConstraint("tenant_id", "company_id"', "notification model")
    require(migration, 'down_revision = "0018_remediation_read_model"', "migration")
    require(migration, '"notification_settings_read"', "migration")

    require(license_router, "from app.routers.notifications import router as notifications_router", "license router")
    require(license_router, "router.include_router(notifications_router)", "license router")
    require(license_router, "router.include_router(remediation_router)", "license router")

    print("PASS: Backend Notification Read Model contract validated.")


if __name__ == "__main__":
    main()
