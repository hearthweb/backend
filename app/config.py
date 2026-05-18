from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Environment(Enum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    # Environment the application is running under
    ENVIRONMENT: Literal[Environment.DEV, Environment.PROD] = Environment.DEV

    # Location for persistent storage
    DATA_DIR: str = "data"

    # Database connection information
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    # Key used for creating JWT tokens; cannot be empty in prod
    SECRET_KEY: str = ""

    # Time (in minutes) that access tokens should be valid for
    ACCESS_TOKEN_LIFETIME: int = 30

    @property
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == Environment.DEV:
            return "sqlite:///{path}".format(
                path=Path(self.DATA_DIR) / "db.sqlite3",
            )
        return "postgresql://{user}:{password}@{host}:{port}/{name}".format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.DB_NAME,
        )


settings = Settings()
