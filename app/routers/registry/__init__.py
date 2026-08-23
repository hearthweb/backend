from fastapi import APIRouter

from . import categories, documents

router = APIRouter(
    prefix="/registry",
    tags=["Registry"],
)

router.include_router(categories.router)
router.include_router(documents.router)
