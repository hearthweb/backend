from fastapi import APIRouter

from .categories import router as category_router
from .credentials import router as credential_router
from .documents import router as document_router

router = APIRouter(prefix="/registry")

router.include_router(category_router)
router.include_router(credential_router)
router.include_router(document_router)
