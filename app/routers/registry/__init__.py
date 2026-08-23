from fastapi import APIRouter

from . import categories, credentials, documents

router = APIRouter(
    prefix="/registry",
    tags=["Registry"],
)

router.include_router(credentials.router)
router.include_router(categories.router)
router.include_router(documents.router)
