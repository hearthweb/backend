from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import Environment, settings
from app.routers import auth, finance, internal, registry, users


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


app.include_router(auth.router)
app.include_router(registry.router)
app.include_router(finance.router)
app.include_router(internal.router)
app.include_router(users.router)
