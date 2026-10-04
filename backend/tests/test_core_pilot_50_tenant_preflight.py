from __future__ import annotations

from app.db import SessionLocal
from app.models import Scan, ScanStartRequest, Tenant


def _start_free_scan(client, tenant: dict[str, str], index: int):
    return client.post(
        "/scan/start",
        headers={
            "X-Tenant-Id": tenant["tenant_id"],
            "X-Api-Token": tenant["api_token"],
        },
        json={
            "tenant_id": tenant["tenant_id"],
            "client_request_id": f"00000000-0000-4000-8000-{index:012d}",
            "run_id": f"PILOT50_{index:03d}",
            "scan_mode": "data_health_score",
            "total_modules": 10,
            "company_name": f"PILOT COMPANY {index:03d}",
            "environment_name": "Sandbox",
        },
    )


def test_fifty_tenants_can_be_admitted_without_cross_tenant_scan_state(client, tenant_factory) -> None:
    tenants = [tenant_factory(tenant_id=f"pilot50_{index:03d}") for index in range(1, 51)]

    responses = [_start_free_scan(client, tenant, index) for index, tenant in enumerate(tenants, start=1)]
    assert all(response.status_code == 200 for response in responses)

    with SessionLocal() as db:
        assert db.query(Tenant).filter(Tenant.tenant_id.like("pilot50_%")).count() == 50
        assert db.query(Scan).filter(Scan.tenant_id.like("pilot50_%")).count() == 50
        assert db.query(ScanStartRequest).filter(ScanStartRequest.tenant_id.like("pilot50_%")).count() == 50

        scan_counts = {
            tenant_id: count
            for tenant_id, count in db.query(Scan.tenant_id, __import__("sqlalchemy").func.count(Scan.id))
            .filter(Scan.tenant_id.like("pilot50_%"))
            .group_by(Scan.tenant_id)
            .all()
        }
        request_counts = {
            tenant_id: count
            for tenant_id, count in db.query(ScanStartRequest.tenant_id, __import__("sqlalchemy").func.count(ScanStartRequest.id))
            .filter(ScanStartRequest.tenant_id.like("pilot50_%"))
            .group_by(ScanStartRequest.tenant_id)
            .all()
        }

    assert len(scan_counts) == len(request_counts) == 50
    assert set(scan_counts) == {tenant["tenant_id"] for tenant in tenants}
    assert all(count == 1 for count in scan_counts.values())
    assert all(count == 1 for count in request_counts.values())
