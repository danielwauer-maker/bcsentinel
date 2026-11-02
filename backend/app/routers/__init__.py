from app.routers.assessment_scope import router as assessment_scope_router
from app.routers.monitoring_reports import router as monitoring_reports_router
from app.routers.reports import router as reports_router
from app.routers.scans import router as scans_router

# Extend canonical routers without changing app.main router wiring.
reports_router.include_router(monitoring_reports_router)
scans_router.include_router(assessment_scope_router)

__all__ = [
    "assessment_scope_router",
    "monitoring_reports_router",
    "reports_router",
    "scans_router",
]
