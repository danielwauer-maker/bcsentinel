from __future__ import annotations

import base64
import json
from types import SimpleNamespace

from app.db import SessionLocal
from app.models import AdminAuditEvent, ImpactSettingsConfig, Tenant, TenantProductEntitlement, TenantScanCredit
from app.services.impact_service import calculate_issue_impact, calculate_scan_commercials
from app.services.product_license_service import build_license_snapshot


def _admin_auth_header() -> dict[str, str]:
    token = base64.b64encode(b"admin-test:admin-password-for-tests-123").decode("ascii")
    return {"Authorization": f"Basic {token}"}


def _admin_csrf(client, path: str = "/admin/config/issue-costs") -> dict[str, str]:
    response = client.get(path, headers=_admin_auth_header())
    assert response.status_code == 200
    token = client.cookies.get("bcs_csrf")
    assert token
    return {"csrf_token": token}


def test_admin_issue_cost_page_lists_estimated_loss_issue_inputs(client):
    response = client.get("/admin/config/issue-costs", headers=_admin_auth_header())

    assert response.status_code == 200
    assert "INTERNAL_HOURLY_RATE_EUR" in response.text
    assert "issue-costs-panel" in response.text
    assert "CUSTOMERS_MISSING_CITY" in response.text
    assert "minutes_per_occurrence" in response.text
    assert "frequency_per_year" in response.text


def test_admin_issue_cost_updates_change_estimated_loss_inputs(client):
    with SessionLocal() as db:
        before = calculate_issue_impact(db, "CUSTOMERS_MISSING_ADDRESS", 2)

    update_response = client.post(
        "/admin/config/issue-costs/CUSTOMERS_MISSING_ADDRESS",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client),
            "title": "Customers missing address",
            "minutes_per_occurrence": "12",
            "probability": "1.0",
            "frequency_per_year": "10",
            "is_active": "on",
        },
        follow_redirects=False,
    )

    hourly_response = client.post(
        "/admin/config/issue-costs/hourly-rate",
        headers=_admin_auth_header(),
        data={**_admin_csrf(client), "hourly_rate_eur": "60"},
        follow_redirects=False,
    )

    assert update_response.status_code == 303
    assert hourly_response.status_code == 303

    with SessionLocal() as db:
        after = calculate_issue_impact(db, "CUSTOMERS_MISSING_ADDRESS", 2)
        hourly_rate = db.get(ImpactSettingsConfig, "default_hourly_rate_eur")

    assert hourly_rate is not None
    assert float(hourly_rate.value_number) == 60.0
    assert after == 240.0
    assert after != before


def test_admin_hourly_rate_changes_estimated_loss_and_potential_saving(client):
    issue = SimpleNamespace(
        code="CUSTOMERS_MISSING_ADDRESS",
        title="Customers missing address",
        category="general",
        severity="medium",
        affected_count=2,
        premium_only=False,
        recommendation_preview=None,
    )

    with SessionLocal() as db:
        before = calculate_scan_commercials(
            db,
            issues=[issue],
            total_records=1000,
            supplied_estimated_premium_price_monthly=99.0,
        )

    hourly_response = client.post(
        "/admin/config/issue-costs/hourly-rate",
        headers=_admin_auth_header(),
        data={**_admin_csrf(client), "hourly_rate_eur": "60"},
        follow_redirects=False,
    )

    assert hourly_response.status_code == 303

    with SessionLocal() as db:
        after = calculate_scan_commercials(
            db,
            issues=[issue],
            total_records=1000,
            supplied_estimated_premium_price_monthly=99.0,
        )

    assert after["estimated_loss_eur"] > before["estimated_loss_eur"]
    assert after["potential_saving_eur"] > before["potential_saving_eur"]


def test_admin_post_without_csrf_is_rejected(client):
    response = client.post(
        "/admin/config/issue-costs/hourly-rate",
        headers=_admin_auth_header(),
        data={"hourly_rate_eur": "60"},
        follow_redirects=False,
    )

    assert response.status_code == 403


def _tenant_csrf(client, tenant_id: str) -> dict[str, str]:
    return _admin_csrf(client, f"/admin/tenants/{tenant_id}")


def _post_tenant_action(client, tenant_id: str, action: str, data: dict | None = None):
    return client.post(
        f"/admin/tenant/{tenant_id}/{action}",
        headers=_admin_auth_header(),
        data={**_tenant_csrf(client, tenant_id), **(data or {})},
        follow_redirects=False,
    )


def _license_snapshot(tenant_id: str) -> dict:
    with SessionLocal() as db:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).one()
        return build_license_snapshot(db, tenant)


def test_admin_product_management_grant_and_revoke_product(client, tenant_factory):
    tenant = tenant_factory()

    grant_response = _post_tenant_action(
        client,
        tenant["tenant_id"],
        "grant-product",
        {"product_code": "assessment"},
    )
    snapshot_after_grant = _license_snapshot(tenant["tenant_id"])

    revoke_response = _post_tenant_action(
        client,
        tenant["tenant_id"],
        "revoke-product",
        {"product_code": "assessment"},
    )
    snapshot_after_revoke = _license_snapshot(tenant["tenant_id"])

    assert grant_response.status_code == 303
    assert snapshot_after_grant["scan_credits_available"] == 1
    assert snapshot_after_grant["assessment_access_active"] is True
    assert revoke_response.status_code == 303
    assert snapshot_after_revoke["scan_credits_available"] == 0
    assert snapshot_after_revoke["assessment_access_active"] is False


def test_admin_scan_credit_management_add_remove_and_reset(client, tenant_factory):
    tenant = tenant_factory()

    add_response = _post_tenant_action(client, tenant["tenant_id"], "add-credit", {"count": "5"})
    remove_response = _post_tenant_action(client, tenant["tenant_id"], "remove-credit", {"count": "1"})
    snapshot_after_remove = _license_snapshot(tenant["tenant_id"])
    reset_response = _post_tenant_action(client, tenant["tenant_id"], "reset-credits")
    snapshot_after_reset = _license_snapshot(tenant["tenant_id"])

    assert add_response.status_code == 303
    assert remove_response.status_code == 303
    assert snapshot_after_remove["scan_credits_available"] == 4
    assert reset_response.status_code == 303
    assert snapshot_after_reset["scan_credits_available"] == 0


def test_admin_monitoring_management_enable_and_disable(client, tenant_factory):
    tenant = tenant_factory()

    enable_response = _post_tenant_action(
        client,
        tenant["tenant_id"],
        "enable-monitoring",
        {"product_code": "monitoring_annual"},
    )
    snapshot_after_enable = _license_snapshot(tenant["tenant_id"])
    disable_response = _post_tenant_action(client, tenant["tenant_id"], "disable-monitoring")
    snapshot_after_disable = _license_snapshot(tenant["tenant_id"])

    assert enable_response.status_code == 303
    assert snapshot_after_enable["monitoring_active"] is True
    assert "monitoring_annual" in snapshot_after_enable["active_products"]
    assert disable_response.status_code == 303
    assert snapshot_after_disable["monitoring_active"] is False


def test_admin_access_management_extend_and_expire(client, tenant_factory):
    tenant = tenant_factory()

    extend_response = _post_tenant_action(client, tenant["tenant_id"], "extend-access", {"days": "7"})
    snapshot_after_extend = _license_snapshot(tenant["tenant_id"])
    expire_response = _post_tenant_action(
        client,
        tenant["tenant_id"],
        "extend-access",
        {"action_value": "expire"},
    )
    snapshot_after_expire = _license_snapshot(tenant["tenant_id"])

    assert extend_response.status_code == 303
    assert snapshot_after_extend["can_view_dashboard"] is True
    assert snapshot_after_extend["dashboard_access_until"]
    assert expire_response.status_code == 303
    assert snapshot_after_expire["can_view_dashboard"] is False
    assert snapshot_after_expire["can_view_issue_details"] is False


def test_admin_reset_licensing_clears_products_monitoring_credits_and_access(client, tenant_factory):
    tenant = tenant_factory()
    _post_tenant_action(client, tenant["tenant_id"], "grant-product", {"product_code": "assessment"})
    _post_tenant_action(client, tenant["tenant_id"], "enable-monitoring", {"product_code": "monitoring_monthly"})
    _post_tenant_action(client, tenant["tenant_id"], "extend-access", {"days": "30"})

    reset_response = _post_tenant_action(client, tenant["tenant_id"], "reset-licensing")
    snapshot = _license_snapshot(tenant["tenant_id"])

    assert reset_response.status_code == 303
    assert snapshot["scan_credits_available"] == 0
    assert snapshot["monitoring_active"] is False
    assert snapshot["can_view_dashboard"] is False
    assert snapshot["active_products"] == []


def test_admin_reset_registration_is_dev_only_and_audited(client, tenant_factory):
    tenant = tenant_factory()

    response = _post_tenant_action(client, tenant["tenant_id"], "reset-registration")

    assert response.status_code == 303
    with SessionLocal() as db:
        row = db.query(Tenant).filter(Tenant.tenant_id == tenant["tenant_id"]).one()
        event = db.query(AdminAuditEvent).filter(AdminAuditEvent.action == "tenant.registration.reset").one()
        assert row.api_token is None
        assert row.api_token_hash is None
        assert row.last_seen_at_utc is None
        assert event.admin_username == "admin-test"


def test_admin_reset_registration_is_blocked_in_production(client, tenant_factory, settings_state):
    tenant = tenant_factory()
    settings_state(ENV="prod")

    response = _post_tenant_action(client, tenant["tenant_id"], "reset-registration")

    assert response.status_code == 403


def _site_translation_fixture(tmp_path, monkeypatch):
    import app.services.site_translation_service as site_translation_service

    landingpage_dir = tmp_path / "landingpage"
    lang_dir = landingpage_dir / "lang"
    lang_dir.mkdir(parents=True)
    de_path = lang_dir / "de.json"
    en_path = lang_dir / "en.json"
    de_path.write_text(
        json.dumps(
            {
                "brand_sub": "Data Quality & Business Impact for Business Central",
                "hero_title": "Deutscher Hero",
                "help_title": "Hilfe",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    en_path.write_text(
        json.dumps(
            {
                "brand_sub": "Data Quality & Business Impact for Business Central",
                "hero_title": "English hero",
                "help_title": "Help",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (landingpage_dir / "index.html").write_text(
        '<span data-i18n="brand_sub"></span><button data-i18n="shared_status_text"></button>',
        encoding="utf-8",
    )
    monkeypatch.setattr(site_translation_service, "LANDINGPAGE_DIR", landingpage_dir)
    monkeypatch.setattr(site_translation_service, "DE_TRANSLATIONS_PATH", de_path)
    monkeypatch.setattr(site_translation_service, "EN_TRANSLATIONS_PATH", en_path)
    return de_path, en_path


def test_admin_site_translations_page_lists_json_and_common_shared_keys(client, tmp_path, monkeypatch):
    _site_translation_fixture(tmp_path, monkeypatch)

    response = client.get("/admin/config/site-translations", headers=_admin_auth_header())

    assert response.status_code == 200
    assert "Uebersetzungen - bcsentinel.com" in response.text
    assert "Common / Shared" in response.text
    assert "brand_sub" in response.text
    assert "hero_title" in response.text
    assert "shared_status_text" in response.text


def test_admin_site_translations_post_updates_de_en_json_and_audits(client, tmp_path, monkeypatch):
    de_path, en_path = _site_translation_fixture(tmp_path, monkeypatch)

    response = client.post(
        "/admin/config/site-translations",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, "/admin/config/site-translations"),
            "keys": ["brand_sub", "hero_title", "help_title"],
            "de_values": ["Claim DE", "Hero DE neu", "Hilfe"],
            "en_values": ["Claim EN", "Hero EN new", "Help"],
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert json.loads(de_path.read_text(encoding="utf-8"))["hero_title"] == "Hero DE neu"
    assert json.loads(en_path.read_text(encoding="utf-8"))["hero_title"] == "Hero EN new"

    with SessionLocal() as db:
        event = db.query(AdminAuditEvent).filter(AdminAuditEvent.action == "update_site_translation").one()
        assert event.admin_username == "admin-test"
        assert "hero_title" in event.details_json


def test_admin_site_translations_rejects_unknown_key_without_write(client, tmp_path, monkeypatch):
    de_path, _ = _site_translation_fixture(tmp_path, monkeypatch)
    before = de_path.read_text(encoding="utf-8")

    response = client.post(
        "/admin/config/site-translations",
        headers=_admin_auth_header(),
        data={
            **_admin_csrf(client, "/admin/config/site-translations"),
            "keys": ["unknown_key"],
            "de_values": ["x"],
            "en_values": ["y"],
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "site_translation_status=error" in response.headers["location"]
    assert de_path.read_text(encoding="utf-8") == before
