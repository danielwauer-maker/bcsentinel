"""Contract tests for the next-generation product policy."""
from datetime import datetime, timedelta, timezone

import pytest

from app.services.access_renewal_policy import (
    ACCESS_DAYS,
    GRANTS,
    Product,
    extend_access,
    new_manual_scan_allowed,
    report_visible,
)

NOW = datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)


def test_free_grants_only_one_scan_and_permanent_free_report():
    assert GRANTS[Product.FREE].additional_scans == 1
    assert GRANTS[Product.FREE].premium_days == 0
    assert GRANTS[Product.FREE].free_report_permanent


def test_full_does_not_grant_new_scan_and_last_fourteen_days():
    assert ACCESS_DAYS == 14
    assert GRANTS[Product.FULL_ASSESSMENT].additional_scans == 0
    assert GRANTS[Product.FULL_ASSESSMENT].premium_days == 14


def test_renewal_variants_have_same_access_but_only_validation_grants_a_scan():
    renewal = GRANTS[Product.ACCESS_RENEWAL]
    validation = GRANTS[Product.ACCESS_RENEWAL_VALIDATION]
    assert renewal.premium_days == validation.premium_days == 14
    assert renewal.additional_scans == 0
    assert validation.additional_scans == 1


def test_extend_starts_from_activation_when_expired():
    assert extend_access(NOW - timedelta(days=3), NOW) == NOW + timedelta(days=14)


def test_extend_stacks_with_remaining_access():
    assert extend_access(NOW + timedelta(days=6), NOW) == NOW + timedelta(days=20)


def test_naive_activation_is_rejected():
    with pytest.raises(ValueError):
        extend_access(None, datetime(2026, 11, 8))


def test_expiry_relocks_premium_reports_but_not_original_free():
    assert report_visible(report_type="free", premium_active=False, monitoring_active=False, is_original_free_report=True)
    assert not report_visible(report_type="free", premium_active=False, monitoring_active=False, is_original_free_report=False)
    assert not report_visible(report_type="full", premium_active=False, monitoring_active=False, is_original_free_report=False)
    assert not report_visible(report_type="validation", premium_active=False, monitoring_active=False, is_original_free_report=False)
    assert report_visible(report_type="full", premium_active=True, monitoring_active=False, is_original_free_report=False)
    assert report_visible(report_type="validation", premium_active=True, monitoring_active=False, is_original_free_report=False)


def test_monitoring_entitles_report_visibility():
    assert report_visible(report_type="monitoring", premium_active=False, monitoring_active=True, is_original_free_report=False)
    assert not report_visible(report_type="monitoring", premium_active=True, monitoring_active=False, is_original_free_report=False)


def test_renewal_without_validation_cannot_launch_scan():
    assert not new_manual_scan_allowed(free_scan_unused=False, validation_credits_available=0, monitoring_active=False)
    assert new_manual_scan_allowed(free_scan_unused=False, validation_credits_available=1, monitoring_active=False)
    assert new_manual_scan_allowed(free_scan_unused=False, validation_credits_available=0, monitoring_active=True)
