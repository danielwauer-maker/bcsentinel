from app.routers.monitoring_reports import router as monitoring_reports_router
from app.routers.reports import router as reports_router

# Extend the canonical /reports router without changing app.main router wiring.
reports_router.include_router(monitoring_reports_router)

__all__ = ["monitoring_reports_router", "reports_router"]
