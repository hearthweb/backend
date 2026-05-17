from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .config import settings
from .database import init_db
from .routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.DATA_DIR).mkdir(
        parents=True,
        exist_ok=True,
    )
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    users.router,
    prefix="/users",
)
