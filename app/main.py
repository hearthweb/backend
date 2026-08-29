from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.auth.routers import router as auth_router
from app.config import Environment, settings
from app.finance.routers import router as finance_router
from app.internal.routers import router as internal_router
from app.registry.routers import router as registry_router


def init():
    """
    Initialize the application
    """
    if settings.ENVIRONMENT == Environment.PROD and settings.SECRET_KEY == "":
        raise RuntimeError("SECRET_KEY must be set in production")
    Path(settings.UPLOAD_DIR).mkdir(
        parents=True,
        exist_ok=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)
app.include_router(registry_router)
app.include_router(finance_router)
app.include_router(internal_router)
