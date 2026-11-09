"""Automatic scope capture must never commit a partially finalized scan."""
from app.db import SessionLocal
from app.models import Scan
from app.assessment_scope_models import AssessmentScopeSnapshot
from app.services.assessment_scope_service import get_or_create_auto_scope


def test_v2_auto_scope_capture_obeys_callers_transaction(tenant_factory, scan_factory):
    tenant_id = tenant_factory()["tenant_id"]
    scan_id = "atomic-scope-persist-1"
    scan_factory(tenant_id=tenant_id, scan_id=scan_id)
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id=scan_id).one()
        scope = get_or_create_auto_scope(db, scan, commit=False)
        assert scope.state == "auto"
        assert scope.tenant_id == tenant_id
        assert scope.included_modules_count >= 1
        assert scope.confirmed_at_utc is None
        assert db.query(AssessmentScopeSnapshot).filter_by(scan_id=scan_id).count() == 1
        # A late scan lease failure/rollback must also discard scope capture.
        db.rollback()
    with SessionLocal() as db:
        assert db.query(AssessmentScopeSnapshot).filter_by(scan_id=scan_id).count() == 0


def test_v2_auto_scope_capture_is_idempotent_for_same_scan(tenant_factory, scan_factory):
    tenant_id = tenant_factory()["tenant_id"]
    scan_id = "atomic-scope-persist-2"
    scan_factory(tenant_id=tenant_id, scan_id=scan_id)
    with SessionLocal() as db:
        scan = db.query(Scan).filter_by(scan_id=scan_id).one()
        first = get_or_create_auto_scope(db, scan, commit=False)
        second = get_or_create_auto_scope(db, scan, commit=False)
        assert first.id == second.id
        assert db.query(AssessmentScopeSnapshot).filter_by(scan_id=scan_id).count() == 1
        db.commit()
    with SessionLocal() as db:
        assert db.query(AssessmentScopeSnapshot).filter_by(scan_id=scan_id).count() == 1
