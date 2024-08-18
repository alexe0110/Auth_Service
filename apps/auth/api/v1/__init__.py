from fastapi import APIRouter

from .account import user_account_router
from .oauth2 import oauth2_router
from .role import role_router

router_v1 = APIRouter(prefix="/v1")
router_v1.include_router(user_account_router)
router_v1.include_router(role_router)
router_v1.include_router(oauth2_router)
