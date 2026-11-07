from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import event

from app.models import ScanRunStatus, Tenant, TenantScanCredit

INITIAL_FREE_SCAN_PRODUCT_CODE = "free_entry"
INITIAL_FREE_SCAN_SOURCE = "tenant_registration"


def _is_registered_free_tenant(tenant: Tenant) -> bool:
    """Return True for the public Extension registration path.

    Registered Extension tenants store only an API token hash (api_token is None),
    start on the free/trial state and must receive exactly one initial Deep Scan.
    Existing test/admin seed helpers that deliberately persist a legacy plaintext
    api_token are not treated as public registrations.
    """

    return (
        tenant.api_token is None
        and bool(tenant.api_token_hash)
        and (tenant.current_plan or "").strip().lower() == "free"
        and (tenant.license_status or "").strip().lower() == "trial"
    )


@event.listens_for(Tenant, "after_insert")
def grant_initial_free_scan_credit(_mapper, connection, tenant: Tenant) -> None:
    """Grant exactly one non-paid Deep Scan credit at tenant registration.

    The credit intentionally uses product_code=free_entry. The existing licensing
    service counts it as an available scan credit, but it does not match the
    Assessment or Validation product codes and therefore cannot unlock paid
    findings, financial values, reports or the seven-day paid-access window.
    The existing scan-start transaction consumes this credit on the first Deep
    Scan, after which another scan requires a paid Validation/Assessment credit
    (where applicable) or active Monitoring.
    """

    if not _is_registered_free_tenant(tenant):
        return

    connection.execute(
        TenantScanCredit.__table__.insert().values(
            tenant_id=tenant.tenant_id,
            product_code=INITIAL_FREE_SCAN_PRODUCT_CODE,
            status="available",
            source=INITIAL_FREE_SCAN_SOURCE,
            source_purchase_id=None,
            consumed_scan_id=None,
            created_at_utc=datetime.now(timezone.utc),
            consumed_at_utc=None,
        )
    )


@event.listens_for(ScanRunStatus, "after_update")
def restore_initial_free_credit_after_failed_scan(_mapper, connection, run: ScanRunStatus) -> None:
    """Return the one Free Entry credit when its scan explicitly fails.

    Credits are consumed at scan start to prevent concurrent duplicate starts.
    A technical failure must not permanently strand a new Free Entry tenant.
    This recovery is deliberately restricted to the `free_entry` registration
    credit; paid Assessment/Validation credit policy remains unchanged.
    """

    if (run.status or "").strip().lower() != "failed":
        return

    connection.execute(
        TenantScanCredit.__table__.update()
        .where(
            TenantScanCredit.tenant_id == run.tenant_id,
            TenantScanCredit.product_code == INITIAL_FREE_SCAN_PRODUCT_CODE,
            TenantScanCredit.status == "consumed",
            TenantScanCredit.consumed_scan_id == run.run_id,
        )
        .values(
            status="available",
            consumed_scan_id=None,
            consumed_at_utc=None,
        )
    )
