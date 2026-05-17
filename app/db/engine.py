from sqlmodel import SQLModel, create_engine

from app.config import Environment, settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == Environment.DEV),
)

SQLModel.metadata.create_all(engine)
