from app.db import SessionLocal
from app.models import Scan
from app.services.product_license_service import PRODUCT_ASSESSMENT, grant_product_entitlement


def _grant_report_access(tenant_id: str) -> None:
    with SessionLocal() as db:
        grant_product_entitlement(db, tenant_id=tenant_id, product_code=PRODUCT_ASSESSMENT, source="test")
        db.commit()


def test_d10_shared_contract_metadata_and_no_legacy_roi(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _grant_report_access(tenant["tenant_id"])
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_d10_contract")
    with SessionLocal() as db:
        scan = db.query(Scan).filter(Scan.scan_id == "scan_d10_contract").one()
        scan.estimated_loss_eur = 10000.0
        scan.potential_saving_eur = 5000.0
        scan.roi_eur = 999999.0
        db.commit()

    response = client.get("/reports/executive/scan_d10_contract", headers=auth_header_factory(tenant))
    assert response.status_code == 200
    payload = response.json()
    assert payload["contract_version"] == "executive-report-v1"
    assert payload["financial_methodology"] == "fin-v1"
    assert payload["report_variant"] == "executive"
    assert payload["dashboard_mode"] == "read_only"
    assert payload["estimated_loss_eur"] == 10000.0
    assert payload["potential_saving_eur"] == 5000.0
    assert payload["validated_improvement_eur"] is None
    assert payload["realized_saving_eur"] is None
    assert "roi_eur" not in payload
    assert "estimated_premium_price_monthly" not in payload


def test_d10_monitoring_projection_uses_same_contract_and_values(client, tenant_factory, auth_header_factory, scan_factory):
    tenant = tenant_factory(plan="free", license_status="active")
    _grant_report_access(tenant["tenant_id"])
    scan_factory(tenant_id=tenant["tenant_id"], scan_id="scan_d10_monitoring")

    executive = client.get("/reports/executive/scan_d10_monitoring", headers=auth_header_factory(tenant))
    monitoring = client.get("/reports/monitoring/scan_d10_monitoring", headers=auth_header_factory(tenant))

    assert executive.status_code == 200
    assert monitoring.status_code == 200
    executive_payload = executive.json()
    monitoring_payload = monitoring.json()
    assert executive_payload["contract_version"] == monitoring_payload["contract_version"]
    assert executive_payload["financial_methodology"] == monitoring_payload["financial_methodology"]
    assert executive_payload["scan_id"] == monitoring_payload["scan_id"]
    assert executive_payload["data_health_score"] == monitoring_payload["data_health_score"]
    assert executive_payload["estimated_loss_eur"] == monitoring_payload["estimated_loss_eur"]
    assert executive_payload["potential_saving_eur"] == monitoring_payload["potential_saving_eur"]
    assert monitoring_payload["report_variant"] == "monitoring"
