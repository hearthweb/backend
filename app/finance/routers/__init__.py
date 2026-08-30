from fastapi import APIRouter

from .accounts import router as account_router
from .transactions import router as transaction_router

router = APIRouter(prefix="/finance")

router.include_router(account_router)
router.include_router(transaction_router)
