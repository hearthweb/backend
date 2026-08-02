from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings


class Environment(Enum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    # Environment the application is running under
    ENVIRONMENT: Environment = Environment.DEV

    # Location for persistent storage
    DATA_DIR: str = "data"

    # Database connection information
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    # Key used for session management; cannot be empty in prod
    SECRET_KEY: str = ""

    @property
    def DATABASE_URL(self) -> str:
        match self.ENVIRONMENT:
            case Environment.PROD:
                return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            case Environment.DEV:
                return f"sqlite:///{Path(self.DATA_DIR) / 'db.sqlite3'}"


settings = Settings()
