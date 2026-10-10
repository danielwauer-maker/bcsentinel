from __future__ import annotations

from datetime import timedelta

import pytest

from app.db import SessionLocal
from app.services.customer_runtime_service import (
    evaluate_connection,
    get_lifecycle,
    lifecycle_access_mode,
    record_connection_diagnostic,
    record_provider_tax_evidence,
    transition_lifecycle,
    upsert_billing_profile,
    utc_now,
)


def test_customer_lifecycle_is_separate_and_transitioned_deterministically(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        initial = get_lifecycle(db, tenant["tenant_id"])
        assert initial.state == "onboarding"
        assert lifecycle_access_mode(initial) == "onboarding_only"
        pilot = transition_lifecycle(
            db,
            tenant_id=tenant["tenant_id"],
            new_state="pilot",
            actor="pytest",
            pilot_until_utc=utc_now() + timedelta(days=60),
        )
        assert pilot.state == "pilot"
        assert lifecycle_access_mode(pilot) == "entitlement_driven"
        with pytest.raises(ValueError, match="not allowed"):
            transition_lifecycle(db, tenant_id=tenant["tenant_id"], new_state="archived", actor="pytest")


def test_payment_failure_maps_to_read_only_grace_not_security_deactivation(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        transition_lifecycle(db, tenant_id=tenant["tenant_id"], new_state="active", actor="pytest")
        row = transition_lifecycle(db, tenant_id=tenant["tenant_id"], new_state="payment_failed", actor="pytest")
        assert lifecycle_access_mode(row) == "read_only_grace"
        assert tenant["tenant_id"] == row.tenant_id


def test_billing_identity_is_tenant_scoped_and_provider_determines_tax(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        row = upsert_billing_profile(
            db,
            tenant_id=tenant["tenant_id"],
            actor="pytest",
            legal_company_name="Contoso GmbH",
            billing_email="billing@contoso.example",
            address_line1="Teststrasse 1",
            postal_code="10115",
            city="Berlin",
            country_code="de",
            vat_id="de123456789",
        )
        assert row.country_code == "DE"
        assert row.vat_id == "DE123456789"
        assert row.tax_treatment == "provider_determined"
        record_provider_tax_evidence(
            db,
            tenant_id=tenant["tenant_id"],
            actor="stripe-webhook",
            provider_customer_id="cus_test",
            tax_treatment="reverse_charge",
            evidence={"source": "stripe", "validated": True},
        )
        assert row.tax_treatment == "reverse_charge"


def test_connection_diagnostics_detect_outdated_extension():
    result = evaluate_connection(
        extension_version="1.0.2.5",
        bc_version="27.0.0.0",
        api_reachable=True,
        permissions_ok=True,
    )
    assert result["status"] == "upgrade_required"
    assert result["upgrade_required"] is True
    assert result["code"] == "EXTENSION_OUTDATED"


def test_connection_diagnostics_detect_permission_failure_before_compatibility():
    result = evaluate_connection(
        extension_version="1.0.2.6",
        bc_version="27.0.0.0",
        api_reachable=True,
        permissions_ok=False,
    )
    assert result["status"] == "blocked"
    assert result["code"] == "PERMISSIONS_MISSING"


def test_connection_diagnostics_accept_current_contract_and_persist(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        row = record_connection_diagnostic(
            db,
            tenant_id=tenant["tenant_id"],
            environment_name="Production",
            company_name="Contoso GmbH",
            extension_version="1.0.2.6",
            bc_version="27.0.0.0",
            api_reachable=True,
            permissions_ok=True,
        )
        db.commit()
        assert row.compatibility_status == "compatible"
        assert row.diagnostic_code == "OK"


def test_billing_profile_requires_iso_country_and_email(tenant_factory):
    tenant = tenant_factory()
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            upsert_billing_profile(
                db,
                tenant_id=tenant["tenant_id"],
                actor="pytest",
                legal_company_name="Contoso",
                billing_email="not-an-email",
                address_line1="Street",
                postal_code="1",
                city="City",
                country_code="Germany",
            )
