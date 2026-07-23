import ast
from pathlib import Path

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.db import Base
from app.models import (
    IssueImpactConfig,
    ProductPricingConfig,
    Scan,
    Tenant,
)


APP_ROOT = Path(__file__).resolve().parents[1] / "app"


def _index_specs(table_name: str) -> dict[str, tuple[tuple[str, ...], bool]]:
    table = Base.metadata.tables[table_name]
    return {
        index.name: (
            tuple(column.name for column in index.columns),
            bool(index.unique),
        )
        for index in table.indexes
    }


def _unique_constraint_names(table_name: str) -> set[str]:
    return {
        constraint.name
        for constraint in Base.metadata.tables[table_name].constraints
        if isinstance(constraint, UniqueConstraint)
    }


def test_gl02a_metadata_defaults_and_names_are_valid():
    assert len(Base.metadata.tables) == 31

    names: set[tuple[str, str]] = set()
    for table in Base.metadata.sorted_tables:
        str(CreateTable(table).compile(dialect=postgresql.dialect()))
        for schema_object in (*table.indexes, *table.constraints):
            if schema_object.name is None:
                continue
            key = (type(schema_object).__name__, schema_object.name)
            assert key not in names
            names.add(key)

    assert str(Scan.__table__.c.premium_available.default.arg) == "False"
    assert str(Scan.__table__.c.premium_available.server_default.arg) == "true"
    assert str(Scan.__table__.c.applied_exception_count.server_default.arg) == "0"
    assert str(IssueImpactConfig.__table__.c.probability.server_default.arg) == "0.2"
    assert str(Tenant.__table__.c.preferred_language.server_default.arg) == "'en'"
    assert str(ProductPricingConfig.__table__.c.updated_at_utc.server_default.arg) == "now()"


def test_gl02a_existing_unique_and_index_groups_are_described_exactly():
    expected_indexes = {
        "dashboard_users": {
            "ix_dashboard_users_email": (("email",), False),
            "uq_dashboard_users_email": (("email",), True),
            "uq_dashboard_users_normalized_email": (("normalized_email",), True),
            "ix_dashboard_users_created_at_utc": (("created_at_utc",), False),
        },
        "dashboard_user_tenant_memberships": {
            "ix_dashboard_memberships_dashboard_user_id": (("dashboard_user_id",), False),
            "ix_dashboard_memberships_tenant_id": (("tenant_id",), False),
            "ix_dashboard_memberships_is_active": (("is_active",), False),
            "ix_dashboard_memberships_last_selected_at_utc": (("last_selected_at_utc",), False),
        },
        "scan_run_statuses": {
            "ix_scan_run_statuses_lease_token": (("lease_token",), False),
            "ix_scan_run_statuses_status_lease": (("status", "lease_expires_at_utc"), False),
            "ix_scan_run_statuses_status_retry": (("status", "next_retry_at_utc"), False),
        },
        "scan_start_requests": {
            "ix_scan_start_requests_scan_id": (("scan_id",), False),
        },
        "landingpage_page_visibility": {
            "ix_landingpage_page_visibility_page_key": (("page_key",), True),
        },
        "partner_referrals": {
            "ix_partner_referrals_tenant_id": (("tenant_id",), True),
        },
        "partner_commissions": {
            "ix_partner_commissions_provider_invoice_id": (("provider_invoice_id",), True),
        },
    }
    for table_name, expected in expected_indexes.items():
        actual = _index_specs(table_name)
        for index_name, specification in expected.items():
            assert actual[index_name] == specification

    expected_constraints = {
        "landingpage_page_visibility": "landingpage_page_visibility_page_key_key",
        "partner_commissions": "partner_commissions_provider_invoice_id_key",
        "partner_referrals": "partner_referrals_tenant_id_key",
        "product_pricing_matrix_config": "uq_product_pricing_matrix_product_tier",
        "scan_run_statuses": "uq_scan_run_statuses_lease_token",
        "scan_start_requests": "uq_scan_start_requests_scan_id",
    }
    for table_name, constraint_name in expected_constraints.items():
        assert constraint_name in _unique_constraint_names(table_name)


def test_gl02a_redundant_primary_key_indexes_are_absent():
    tables = {
        "credit_ledger_entries",
        "dashboard_user_tenant_memberships",
        "scan_start_requests",
        "tenant_product_entitlements",
        "tenant_product_purchases",
        "tenant_scan_credits",
    }
    for table_name in tables:
        assert not any(
            tuple(column.name for column in index.columns) == ("id",)
            for index in Base.metadata.tables[table_name].indexes
        )


def test_gl02a_production_scan_inserts_set_premium_available_explicitly():
    scan_calls: list[tuple[Path, ast.Call]] = []
    for source_path in APP_ROOT.rglob("*.py"):
        source = source_path.read_text(encoding="utf-8-sig")
        assert "insert into scans" not in source.lower()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Scan":
                scan_calls.append((source_path.relative_to(APP_ROOT), node))

    assert {str(path).replace("\\", "/") for path, _ in scan_calls} == {
        "main.py",
        "routers/scans.py",
        "services/atomic_scan_start_service.py",
    }
    assert all(
        "premium_available" in {keyword.arg for keyword in call.keywords}
        for _, call in scan_calls
    )

    main_source = (APP_ROOT / "main.py").read_text(encoding="utf-8")
    scan_router_source = (APP_ROOT / "routers" / "scans.py").read_text(encoding="utf-8")
    atomic_source = (
        APP_ROOT / "services" / "atomic_scan_start_service.py"
    ).read_text(encoding="utf-8")
    derived_assignment = (
        "scan.premium_available = is_premium_actions_enabled(tenant_features)"
    )
    assert derived_assignment in main_source
    assert derived_assignment in scan_router_source
    assert 'premium_available=requested_mode != "data_health_score"' in atomic_source
