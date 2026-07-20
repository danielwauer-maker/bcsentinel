from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from jose import jwt

from app.core.settings import settings
from app.db import SessionLocal
from app.models import TenantProductEntitlement
from app.routers.reports import REPORT_SHARE_ALGORITHM
from app.services.access_control_service import (
    ACCESS_SNAPSHOT_TTL_SECONDS,
    ACCESS_SNAPSHOT_VERSION,
    TOKEN_AUDIENCE,
)

ROOT = Path(__file__).resolve().parents[2]


def _grant(tenant_id: str, *, days: int = 7) -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(
            TenantProductEntitlement(
                tenant_id=tenant_id,
                product_code="full_analysis",
                status="active",
                source="p0d_test",
                valid_until_utc=now + timedelta(days=days),
                created_at_utc=now,
                updated_at_utc=now,
            )
        )
        db.commit()


def _revoke(tenant_id: str) -> None:
    with SessionLocal() as db:
        entitlement = db.query(TenantProductEntitlement).filter_by(tenant_id=tenant_id).one()
        entitlement.status = "revoked"
        entitlement.updated_at_utc = datetime.now(timezone.utc)
        db.commit()


@pytest.mark.parametrize(
    "capability",
    [
        "product_access",
        "dashboard_access",
        "issues_access",
        "report_access",
        "monitoring_access",
        "subscription_active",
        "scan_start_access",
    ],
)
def test_snapshot_contains_canonical_capability(client, tenant_factory, auth_header_factory, capability):
    tenant = tenant_factory()
    response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    decision = response.json()["capabilities"][capability]
    assert set(decision) == {"granted", "valid_from_utc", "valid_until_utc", "end_inclusive", "reason_code"}


@pytest.mark.parametrize(
    "capability",
    ["product_access", "dashboard_access", "issues_access", "report_access", "monitoring_access", "subscription_active"],
)
def test_free_snapshot_denies_protected_capability(client, tenant_factory, auth_header_factory, capability):
    tenant = tenant_factory()
    response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert response.json()["capabilities"][capability]["granted"] is False


@pytest.mark.parametrize("capability", ["product_access", "dashboard_access", "issues_access", "report_access"])
def test_full_analysis_grants_detail_capability(client, tenant_factory, auth_header_factory, capability):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"])
    response = client.get("/license/status", headers=auth_header_factory(tenant))
    assert response.json()["capabilities"][capability]["granted"] is True


def test_snapshot_metadata_is_short_lived_and_correlated(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    response = client.get("/license/status", headers=auth_header_factory(tenant))
    payload = response.json()
    server_time = datetime.fromisoformat(payload["current_time_utc"])
    expires_at = datetime.fromisoformat(payload["snapshot_expires_at_utc"])
    assert payload["snapshot_version"] == ACCESS_SNAPSHOT_VERSION
    assert payload["cache_ttl_seconds"] == ACCESS_SNAPSHOT_TTL_SECONDS
    assert (expires_at - server_time).total_seconds() == ACCESS_SNAPSHOT_TTL_SECONDS
    assert payload["correlation_id"]
    assert payload["tenant_context"]["tenant_id"] == tenant["tenant_id"]


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/analytics/get-token"),
        ("get", "/reports/executive/P0D_SCAN"),
        ("get", "/reports/executive/P0D_SCAN/html"),
        ("get", "/reports/executive/P0D_SCAN/pdf"),
        ("post", "/reports/executive/P0D_SCAN/share-link"),
    ],
)
def test_protected_endpoint_is_403_without_capability(
    client, tenant_factory, auth_header_factory, scan_factory, method, path
):
    tenant = tenant_factory()
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="P0D_SCAN")
    response = getattr(client, method)(path, headers=auth_header_factory(tenant))
    assert response.status_code == 403
    assert "capability" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "claim",
    ["type", "tenant_id", "company_id", "capability", "scope", "aud", "iat", "exp"],
)
def test_dashboard_token_has_security_claim(client, tenant_factory, auth_header_factory, claim):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"])
    response = client.get("/analytics/get-token", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    payload = jwt.decode(
        response.json()["token"],
        settings.SECRET_KEY,
        algorithms=["HS256"],
        audience=TOKEN_AUDIENCE,
    )
    assert claim in payload


def test_dashboard_token_revocation_is_rechecked(client, tenant_factory, auth_header_factory):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"])
    token = client.get("/analytics/get-token", headers=auth_header_factory(tenant)).json()["token"]
    _revoke(tenant["tenant_id"])
    response = client.get("/analytics/embed/data", params={"embed_token": token})
    assert response.status_code == 403


def test_report_token_revocation_is_rechecked(
    client, tenant_factory, auth_header_factory, scan_factory
):
    tenant = tenant_factory()
    _grant(tenant["tenant_id"])
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="P0D_REPORT")
    share = client.post(
        "/reports/executive/P0D_REPORT/share-link",
        headers=auth_header_factory(tenant),
        json={"report_type": "html"},
    )
    assert share.status_code == 200
    token = share.json()["url"].split("token=", 1)[1]
    claims = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[REPORT_SHARE_ALGORITHM],
        audience=TOKEN_AUDIENCE,
    )
    assert claims["capability"] == "report_access"
    assert claims["iat"] < claims["exp"]
    _revoke(tenant["tenant_id"])
    response = client.get(
        "/reports/executive/P0D_REPORT/html/shared",
        params={"token": token},
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "relative_path",
    [
        "bc-extension/app/src/pages/DHDeepScanFindings.Page.al",
        "bc-extension/app/src/pages/DHDeepScanFindingsList.Page.al",
        "bc-extension/app/src/pages/DHDashboardIssues.Page.al",
        "bc-extension/app/src/pages/DHDashboardIssuesList.Page.al",
        "bc-extension/app/src/pages/DHScanIssues.Page.al",
        "bc-extension/app/src/pages/DHIssuesPart.Page.al",
        "bc-extension/app/src/pages/DHCustomerIssueList.Page.al",
        "bc-extension/app/src/pages/DHVendorIssueList.Page.al",
        "bc-extension/app/src/pages/DHItemNegativeInventoryList.Page.al",
        "bc-extension/app/src/pages/DHItemMissingCostList.Page.al",
        "bc-extension/app/src/pages/DHItemMissingPriceList.Page.al",
        "bc-extension/app/src/pages/DHBlockedItemsWithInventory.Page.al",
        "bc-extension/app/src/pages/DHPurchaseLineIssueWorklist.Page.al",
        "bc-extension/app/src/pages/DHSalesLineIssueWorklist.Page.al",
        "bc-extension/app/src/pages/DHDuplicateWorklist.Page.al",
    ],
)
def test_direct_protected_page_has_open_guard(relative_path):
    source = (ROOT / relative_path).read_text(encoding="utf-8")
    assert "trigger OnOpenPage()" in source
    assert "AccessGuard.EnsureIssuesAccess();" in source


def test_al_guard_forces_fresh_check_and_fails_closed():
    source = (ROOT / "bc-extension/app/src/codeunits/DHAccessGuard.Codeunit.al").read_text(encoding="utf-8")
    assert "EnsureCapability('issues_access', true);" in source
    assert "TryRefreshAccessSnapshot" in source
    assert "Error(AccessNotVerifiedErr);" in source
    assert "60000" in source


def test_partial_response_cannot_preserve_positive_cache():
    source = (ROOT / "bc-extension/app/src/codeunits/DHApiClient.Codeunit.al").read_text(encoding="utf-8")
    refresh = source[source.index("procedure RefreshLicenseStatus"):]
    invalidation = refresh.index("Setup.InvalidateAccessSnapshot();")
    request = refresh.index("Client.Get(")
    assert invalidation < request
    assert "incomplete capability set" in refresh


def test_viewer_has_no_direct_protected_table_reads():
    source = (ROOT / "bc-extension/app/src/permissionsets/BCSentinelPermissionSets.al").read_text(encoding="utf-8")
    viewer = source.split('permissionset 53191 "BCSENTINEL SCAN"', 1)[0]
    assert 'tabledata "DH Scan Issue"' not in viewer
    assert 'tabledata "DH Deep Scan Finding"' not in viewer
    assert 'tabledata "DH Dashboard Issue"' not in viewer
    assert 'codeunit "DH Access Guard" = X' in viewer
