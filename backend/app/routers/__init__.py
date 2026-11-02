from app.routers.assessment_scope import router as assessment_scope_router
from app.routers.monitoring_reports import router as monitoring_reports_router
from app.routers import reports as reports_module
from app.routers.reports import router as reports_router
from app.routers.scans import router as scans_router
from app.services.validation_scope_report_service import build_validation_report as build_scoped_validation_report

# Extend canonical routers without changing app.main router wiring.
reports_router.include_router(monitoring_reports_router)
scans_router.include_router(assessment_scope_router)

# reports.py historically imports the Validation builder as a module global.
# Keep all existing JSON/HTML/PDF/share routes intact while replacing that
# builder with the scope-aware v1 overlay at runtime.
reports_module.build_validation_report = build_scoped_validation_report

__all__ = [
    "assessment_scope_router",
    "monitoring_reports_router",
    "reports_router",
    "scans_router",
]
