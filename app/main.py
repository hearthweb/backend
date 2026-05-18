from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import Environment, settings
from app.database import init_db
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == Environment.PROD and settings.SECRET_KEY == "":
        raise RuntimeError("SECRET_KEY must be set in production")
    Path(settings.DATA_DIR).mkdir(
        parents=True,
        exist_ok=True,
    )
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

app.include_router(
    auth.router,
    prefix="/auth",
)

app.include_router(
    users.router,
    prefix="/users",
)
