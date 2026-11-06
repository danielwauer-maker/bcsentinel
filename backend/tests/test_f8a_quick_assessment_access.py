from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import Tenant, TenantProductEntitlement, TenantScanCredit
from app.services.product_license_service import grant_product_entitlement
from app.services.quick_assessment_access_service import PRODUCT_QUICK_ASSESSMENT


def _grant(tenant_id: str, product_code: str, *, valid_until: datetime | None) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(
            db,
            tenant_id=tenant_id,
            product_code=product_code,
            source="f8_test",
            valid_until_utc=valid_until,
        )
        db.commit()


def test_quick_assessment_entitlement_adds_only_quick_capabilities_without_scan_credit(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        db.query(TenantScanCredit).filter(TenantScanCredit.tenant_id == tenant["tenant_id"]).delete()
        db.commit()

    _grant(
        tenant["tenant_id"],
        PRODUCT_QUICK_ASSESSMENT,
        valid_until=now + timedelta(days=7),
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert PRODUCT_QUICK_ASSESSMENT in payload["active_products"]
    assert payload["quick_assessment_entitlement_active"] is True
    assert payload["quick_assessment_access_active"] is True
    assert payload["can_view_quick_assessment"] is True
    assert payload["can_view_quick_findings"] is True
    assert "quick_assessment" in payload["features"]
    assert "quick_assessment_findings" in payload["features"]

    # Quick is an access layer over the existing scan, not a new scan product.
    assert payload["scan_credits_available"] == 0
    assert payload["can_run_deep_scan"] is False

    # Quick must never inherit Full Assessment / Validation detail privileges.
    assert payload["assessment_access_active"] is False
    assert payload["validation_access_active"] is False
    assert payload["can_view_dashboard"] is False
    assert payload["can_view_issue_details"] is False
    assert "executive_report" not in payload["features"]
    assert "recommendations" not in payload["features"]

    with SessionLocal() as db:
        assert (
            db.query(TenantScanCredit)
            .filter(TenantScanCredit.tenant_id == tenant["tenant_id"])
            .count()
            == 0
        )


def test_expired_quick_assessment_entitlement_does_not_grant_access(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    _grant(
        tenant["tenant_id"],
        PRODUCT_QUICK_ASSESSMENT,
        valid_until=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert PRODUCT_QUICK_ASSESSMENT not in payload["active_products"]
    assert payload["quick_assessment_entitlement_active"] is False
    assert payload["quick_assessment_access_active"] is False
    assert payload["can_view_quick_assessment"] is False
    assert payload["can_view_quick_findings"] is False
    assert "quick_assessment" not in payload["features"]


def test_full_assessment_implies_quick_level_capability_without_quick_entitlement(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    _grant(
        tenant["tenant_id"],
        "assessment",
        valid_until=datetime.now(timezone.utc) + timedelta(days=7),
    )

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["quick_assessment_entitlement_active"] is False
    assert payload["quick_assessment_access_active"] is True
    assert payload["can_view_quick_assessment"] is True
    assert payload["can_view_quick_findings"] is True
    assert payload["assessment_access_active"] is True
    assert "quick_assessment" in payload["features"]


def test_quick_assessment_without_expiry_is_supported_as_explicit_entitlement_state(
    client,
    tenant_factory,
    auth_header_factory,
):
    tenant = tenant_factory(plan="free", license_status="trial")
    _grant(tenant["tenant_id"], PRODUCT_QUICK_ASSESSMENT, valid_until=None)

    response = client.get("/license/status", headers=auth_header_factory(tenant))

    assert response.status_code == 200
    payload = response.json()
    assert payload["quick_assessment_entitlement_active"] is True
    assert payload["quick_assessment_access_active"] is True
    assert payload["quick_assessment_access_until"] is None
