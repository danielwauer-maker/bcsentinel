from fastapi import APIRouter

from app.routers.account_auth import router as account_auth_router
from app.routers.auth import router as tenant_auth_router

router = APIRouter()
router.include_router(tenant_auth_router)
router.include_router(account_auth_router)
