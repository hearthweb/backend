from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import Environment, settings
from app.routers import auth, users


def init():
    """
    Initialize the application
    """
    if settings.ENVIRONMENT == Environment.PROD and settings.SECRET_KEY == "":
        raise RuntimeError("SECRET_KEY must be set in production")
    Path(settings.DATA_DIR).mkdir(
        parents=True,
        exist_ok=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(users.router)
