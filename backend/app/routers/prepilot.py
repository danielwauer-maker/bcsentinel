from fastapi import APIRouter

from app.routers.account_auth import router as account_auth_router
from app.routers.commercial_admin import router as commercial_admin_router
from app.routers.commercial_billing import router as commercial_billing_router
from app.routers.customer_runtime import router as customer_runtime_router
from app.routers.membership_admin import router as membership_admin_router
from app.routers.operations_governance import router as operations_governance_router

# Tenant auth is already mounted by the license router. This aggregator contains
# only the newer account/commercial/operations surfaces so it can be mounted
# exactly once without duplicating /auth/session.
router = APIRouter()
router.include_router(account_auth_router)
router.include_router(membership_admin_router)
router.include_router(customer_runtime_router)
router.include_router(operations_governance_router)
router.include_router(commercial_admin_router)
router.include_router(commercial_billing_router)
