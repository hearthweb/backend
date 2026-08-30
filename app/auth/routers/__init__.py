from fastapi import APIRouter

from .sessions import router as session_router
from .users import router as user_router

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(session_router)
router.include_router(user_router)
