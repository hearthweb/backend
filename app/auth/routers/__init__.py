from fastapi import APIRouter

from .roles import router as role_router
from .sessions import router as session_router
from .users import router as user_router

router = APIRouter(prefix="/auth")

router.include_router(role_router)
router.include_router(session_router)
router.include_router(user_router)
