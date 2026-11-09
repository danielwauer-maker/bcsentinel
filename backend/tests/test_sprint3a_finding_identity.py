import pytest
from fastapi import HTTPException

from app.core.settings import settings
from app.db import SessionLocal
from app.models import ScanIssueRecord
from app.services.monitoring_report_service import _issue_maps
from app.services.validation_report_service import _issue_map


def test_v2_rejects_ambiguous_duplicate_check_codes(monkeypatch, tenant_factory, scan_factory):
    monkeypatch.setattr(settings, "ACCESS_MODEL_V2_ENABLED", True)
    tenant = tenant_factory()
    scan_id = "sprint3a-ambiguous-findings"
    scan_factory(tenant_id=tenant["tenant_id"], scan_id=scan_id)
    with SessionLocal() as db:
        for finding_id in ("synthetic-id-1", "synthetic-id-2"):
            db.add(ScanIssueRecord(scan_id=scan_id, finding_id=finding_id, code="SAME-CHECK", title="test", severity="high", affected_count=1))
        db.flush()
        for load in (lambda: _issue_map(db, scan_id), lambda: _issue_maps(db, [scan_id])):
            with pytest.raises(HTTPException) as error:
                load()
            assert error.value.status_code == 409
            assert "ambiguous finding identity" in error.value.detail
        db.rollback()
