from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Environment, settings
from app.database import init_db
from app.routers import auth, users
from app.utils import init_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == Environment.PROD and settings.SECRET_KEY == "":
        raise RuntimeError("SECRET_KEY must be set in production")
    init_data()
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(users.router)
