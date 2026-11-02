from datetime import datetime, timezone

from app.models import Scan, Tenant
from app.services.assessment_scope_service import confirm_scope, get_or_create_auto_scope, included_module_codes


def _tenant() -> Tenant:
    now = datetime.now(timezone.utc)
    return Tenant(
        tenant_id="tenant-scope",
        api_token="tok_scope_test",
        environment_name="test",
        app_version="1.0.0",
        created_at_utc=now,
        last_seen_at_utc=now,
        current_plan="free",
        license_status="active",
    )


def _scan() -> Scan:
    return Scan(
        scan_id="scope-test-1",
        tenant_id="tenant-scope",
        scan_type="deep",
        generated_at_utc=datetime.now(timezone.utc),
        data_score=55,
        checks_count=199,
        issues_count=10,
        premium_available=True,
        summary_headline="test",
        summary_rating="test",
        system_score=90,
        finance_score=80,
        sales_score=70,
        purchasing_score=60,
        inventory_score=50,
        crm_score=40,
        manufacturing_score=30,
        service_score=20,
        jobs_score=10,
        hr_score=0,
        gl_entries_count=100,
        customers_count=10,
        sales_headers_count=5,
        vendors_count=0,
        purchase_headers_count=0,
        items_count=20,
        item_ledger_entries_count=100,
    )


def _persist_scan(db_session, scan_id: str) -> Scan:
    db_session.add(_tenant())
    scan = _scan()
    scan.scan_id = scan_id
    db_session.add(scan)
    db_session.commit()
    return scan


def test_auto_scope_scores_only_detected_active_standard_modules(db_session):
    scan = _persist_scan(db_session, "scope-test-1")

    scope = get_or_create_auto_scope(db_session, scan)
    included = included_module_codes(scope)

    assert included == {"system", "finance", "sales", "inventory"}
    assert scope.score_type == "preliminary"
    assert scope.score_value == 73  # round((90 + 80 + 70 + 50) / 4)
    assert scope.unknown_modules_count == 5


def test_full_scope_confirmation_recalculates_without_new_scan(db_session):
    scan = _persist_scan(db_session, "scope-test-2")

    auto = get_or_create_auto_scope(db_session, scan)
    confirmed = confirm_scope(
        db_session,
        scan,
        {
            "crm": "include",
            "purchasing": "exclude",
            "manufacturing": "exclude",
            "service": "exclude",
            "jobs": "exclude",
            "hr": "exclude",
        },
    )

    assert confirmed.scan_id == auto.scan_id
    assert confirmed.version == auto.version + 1
    assert confirmed.state == "confirmed"
    assert confirmed.score_type == "confirmed_baseline"
    assert included_module_codes(confirmed) == {"system", "finance", "sales", "inventory", "crm"}
    assert confirmed.score_value == 66  # round((90 + 80 + 70 + 50 + 40) / 5)


def test_custom_extensions_are_not_part_of_score(db_session):
    scan = _persist_scan(db_session, "scope-test-3")

    scope = get_or_create_auto_scope(db_session, scan)
    assert scope.unsupported_extensions_json == "[]"
    assert all(module.support_status == "supported" for module in scope.modules)
