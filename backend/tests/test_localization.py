from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Scan, ScanIssueRecord, Tenant
from app.security.token_hash import hash_api_token
from app.services.executive_report_service import build_executive_report
from app.services.localization_service import normalize_language


def test_normalize_language_maps_german_variants_to_de():
    assert normalize_language("de-DE") == "de"
    assert normalize_language("de_AT") == "de"
    assert normalize_language("de-CH") == "de"
    assert normalize_language("de") == "de"


def test_normalize_language_defaults_non_german_to_en():
    assert normalize_language("en-US") == "en"
    assert normalize_language("fr-FR") == "en"
    assert normalize_language(None) == "en"


def test_tenant_registration_sets_de_for_de_de(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json={"environment_name": "BC Cloud", "app_version": "1.0.0", "preferred_language": "de-DE"},
    )

    assert response.status_code == 200
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == response.json()["tenant_id"]))
        assert tenant is not None
        assert tenant.preferred_language == "de"


def test_tenant_registration_sets_en_for_en_us(client, settings_state):
    settings_state(TENANT_REGISTRATION_INVITE_CODE="pilot-secret")

    response = client.post(
        "/tenant/register",
        headers={"X-Registration-Invite": "pilot-secret"},
        json={"environment_name": "BC Cloud", "app_version": "1.0.0", "preferred_language": "en-US"},
    )

    assert response.status_code == 200
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == response.json()["tenant_id"]))
        assert tenant is not None
        assert tenant.preferred_language == "en"


def test_license_refresh_updates_preferred_language(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    headers = auth_header_factory(tenant)
    headers["X-Preferred-Language"] = "de-CH"

    response = client.get("/license/status", headers=headers)

    assert response.status_code == 200
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row is not None
        assert row.preferred_language == "de"


def test_analytics_payload_uses_tenant_language(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        row = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant["tenant_id"]))
        assert row is not None
        row.preferred_language = "de"
        db.commit()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_lang_de")

    token_response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert token_response.status_code == 200
    embed_token = token_response.json()["token"]
    response = client.get("/analytics/embed/data", params={"embed_token": embed_token})

    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "de"
    assert body["ui"]["overview"] == "Ueberblick"


def test_executive_report_uses_tenant_language():
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        tenant = Tenant(
            tenant_id="ten_report_de",
            api_token=None,
            api_token_hash=hash_api_token("tok_report_de"),
            environment_name="BC Cloud",
            app_version="1.0.0",
            preferred_language="de",
            created_at_utc=now,
            last_seen_at_utc=now,
            current_plan="free",
            license_status="trial",
        )
        db.add(tenant)
        db.add(
            Scan(
                scan_id="scan_report_de",
                tenant_id=tenant.tenant_id,
                scan_type="deep",
                generated_at_utc=now,
                data_score=58,
                checks_count=10,
                issues_count=1,
                premium_available=True,
                summary_headline="headline",
                summary_rating="rating",
                total_records=100,
                estimated_loss_eur=1000.0,
                potential_saving_eur=500.0,
                estimated_premium_price_monthly=99.0,
                roi_eur=0.0,
            )
        )
        db.add(
            ScanIssueRecord(
                scan_id="scan_report_de",
                code="CUSTOMERS_MISSING_EMAIL",
                title="Missing e-mail",
                severity="high",
                affected_count=3,
                estimated_impact_eur=100.0,
            )
        )
        db.commit()

        report = build_executive_report(db, tenant, "scan_report_de")

    assert report.language == "de"
    assert "geschaetzten Jahresimpact" in report.executive_summary
    assert report.score_status == "Kritisch"
