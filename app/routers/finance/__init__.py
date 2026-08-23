from fastapi import APIRouter

from . import accounts, transactions

router = APIRouter(
    prefix="/finance",
    tags=["Finance"],
)

router.include_router(accounts.router)
router.include_router(transactions.router)
