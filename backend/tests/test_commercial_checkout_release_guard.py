"""The new commercial checkout route stays dark until separately approved.

Legacy checkout and existing entitlements are intentionally not changed by
this flag; that path has distinct contractual and refund lifecycle tests.
"""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.routers.commercial_billing import create_commercial_checkout_session


def test_commercial_checkout_is_default_disabled(monkeypatch):
    monkeypatch.setattr(settings, "COMMERCIAL_CHECKOUT_ENABLED", False)
    # The gate must run before database, authentication or Stripe side effects.
    with pytest.raises(HTTPException) as err:
        create_commercial_checkout_session(
            SimpleNamespace(tenant_id="pilot-tenant", product_code="full_analysis"),
            tenant_auth=("pilot-tenant", "unused-test-token"),
        )
    assert err.value.status_code == 503
    assert "not released" in str(err.value.detail)


def test_commercial_checkout_flag_default_is_false():
    from app.core.settings import Settings

    assert Settings.model_fields["COMMERCIAL_CHECKOUT_ENABLED"].default is False
