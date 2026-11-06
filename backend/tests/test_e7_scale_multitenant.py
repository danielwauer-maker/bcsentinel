from __future__ import annotations

import pytest

from app.db import SessionLocal
from app.routers import account_auth
from app.security.oidc import VerifiedOIDCIdentity
from app.services.account_membership_service import get_or_create_user_identity, upsert_tenant_membership


def _identity() -> VerifiedOIDCIdentity:
    return VerifiedOIDCIdentity(
        provider="test-oidc",
        subject="e7-scale-subject",
        email="scale.account@example.com",
        display_name="E7 Scale Account",
    )


def _seed_account_memberships(tenants: list[dict]) -> None:
    with SessionLocal() as db:
        user = get_or_create_user_identity(
            db,
            provider="test-oidc",
            provider_subject="e7-scale-subject",
            email="scale.account@example.com",
            display_name="E7 Scale Account",
        )
        for index, tenant in enumerate(tenants):
            upsert_tenant_membership(
                db,
                user_identity_id=user.id,
                tenant_id=tenant["tenant_id"],
                role="ADMIN" if index % 2 == 0 else "VIEWER",
                status="active",
            )
        db.commit()


def _select_tenant(client, account_token: str, tenant_id: str) -> tuple[str, dict]:
    response = client.post(
        "/auth/account/tenant-session",
        json={"tenant_id": tenant_id},
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    return body["session_token"], body


@pytest.mark.parametrize("tenant_count", [1, 5, 10, 25, 50])
def test_account_scale_matrix_preserves_tenant_scope(
    client,
    monkeypatch,
    tenant_factory,
    tenant_count: int,
):
    tenants: list[dict] = []
    for index in range(tenant_count):
        tenants.append(
            tenant_factory(
                tenant_id=f"ten_e7_{tenant_count}_{index:02d}",
                plan="premium" if index % 3 == 0 else "free",
                license_status="active" if index % 3 == 0 else "trial",
            )
        )
    _seed_account_memberships(tenants)
    monkeypatch.setattr(account_auth, "verify_oidc_bearer_token", lambda token: _identity())

    login = client.post("/auth/account/session", headers={"Authorization": "Bearer e7-external-token"})
    assert login.status_code == 200, login.text
    account = login.json()
    assert account["tenant_count"] == tenant_count
    assert account["requires_tenant_selection"] is (tenant_count > 1)
    account_token = account["session_token"]

    listing = client.get(
        "/auth/account/tenants",
        headers={"Authorization": f"Bearer {account_token}"},
    )
    assert listing.status_code == 200, listing.text
    listed = listing.json()["tenants"]
    assert len(listed) == tenant_count
    listed_by_id = {item["tenant_id"]: item for item in listed}
    assert set(listed_by_id) == {tenant["tenant_id"] for tenant in tenants}

    # Exercise representative tenant switches for every matrix size. At 50
    # tenants this hits both ends and the middle without converting a CI
    # correctness gate into a fragile benchmark.
    sample_indexes = sorted({0, tenant_count // 2, tenant_count - 1})
    sessions: dict[int, str] = {}
    for index in sample_indexes:
        tenant = tenants[index]
        token, session = _select_tenant(client, account_token, tenant["tenant_id"])
        sessions[index] = token
        assert session["tenant_id"] == tenant["tenant_id"]
        assert session["role"] == ("ADMIN" if index % 2 == 0 else "VIEWER")

        status = client.get(
            "/billing/subscription/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert status.status_code == 200, status.text
        assert status.json()["tenant_id"] == tenant["tenant_id"]

    # Switching later must not mutate a previously minted tenant session.
    first_token = sessions[0]
    first_status_after_switches = client.get(
        "/billing/subscription/status",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert first_status_after_switches.status_code == 200
    assert first_status_after_switches.json()["tenant_id"] == tenants[0]["tenant_id"]

    if tenant_count > 1:
        last_index = tenant_count - 1
        last_token = sessions[last_index]
        mixed = client.get(
            "/billing/subscription/status",
            headers={
                "Authorization": f"Bearer {last_token}",
                "X-Tenant-Id": tenants[0]["tenant_id"],
            },
        )
        assert mixed.status_code == 403
