"""Unreleased commercial-session route is fail-closed regardless of settings.

This reserved API must not perform DB/Stripe IO until its pricing and payment
contract has been implemented and separately approved. Legacy billing is intact.
"""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.routers.commercial_billing import create_commercial_checkout_session


@pytest.mark.parametrize("enabled", [False, True])
def test_commercial_checkout_fails_closed_regardless_of_flag(monkeypatch, enabled):
    monkeypatch.setattr(settings, "COMMERCIAL_CHECKOUT_ENABLED", enabled)
    with pytest.raises(HTTPException) as err:
        create_commercial_checkout_session(
            SimpleNamespace(tenant_id="pilot-tenant", product_code="full_analysis"),
            tenant_auth=("pilot-tenant", "unused-test-token"),
        )
    assert err.value.status_code == 503
    assert err.value.detail == "Commercial checkout is not released."


def test_commercial_checkout_flag_default_is_false():
    from app.core.settings import Settings

    assert Settings.model_fields["COMMERCIAL_CHECKOUT_ENABLED"].default is False


def test_commercial_checkout_endpoint_refuses_stripe_even_when_flag_enabled(client, monkeypatch):
    monkeypatch.setattr(settings, "COMMERCIAL_CHECKOUT_ENABLED", True)
    response = client.post(
        "/billing/checkout/commercial-session",
        json={"tenant_id": "pilot-tenant", "product_code": "full_analysis"},
        headers={"X-Tenant-Id": "pilot-tenant", "X-Api-Token": "unused-test-token"},
    )
    # Authentication may reject the fake token first; must never return a checkout session.
    assert response.status_code in (401, 403, 422, 503)
    assert "checkout_url" not in response.text
