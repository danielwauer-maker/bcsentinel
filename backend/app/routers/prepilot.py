from fastapi import APIRouter

from app.routers.account_auth import router as account_auth_router
from app.routers.auth import router as tenant_auth_router
from app.routers.customer_runtime import router as customer_runtime_router
from app.routers.membership_admin import router as membership_admin_router
from app.routers.operations_governance import router as operations_governance_router

router = APIRouter()
router.include_router(tenant_auth_router)
router.include_router(account_auth_router)
router.include_router(membership_admin_router)
router.include_router(customer_runtime_router)
router.include_router(operations_governance_router)
