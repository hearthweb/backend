from enum import Enum

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Environment(Enum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    # Environment the application is running under
    ENVIRONMENT: Environment = Environment.DEV

    # Location for uploaded files
    UPLOAD_DIR: str = "upload"

    # Database connection information
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    # Key used for session management; cannot be empty in prod
    SECRET_KEY: str = ""

    # Key used for encrypting TOTP secrets; cannot be empty in prod
    TOTP_ENCRYPTION_KEY: str = ""

    @property
    def DATABASE_URL(self) -> str:
        match self.ENVIRONMENT:
            case Environment.PROD:
                return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            case Environment.DEV:
                return f"sqlite:///{'db.sqlite3'}"

    @model_validator(mode="after")
    def validate_prod_keys(self) -> Settings:
        match self.ENVIRONMENT:
            case Environment.PROD:
                if settings.SECRET_KEY == "":
                    raise RuntimeError("SECRET_KEY must be set in production")
                if settings.TOTP_ENCRYPTION_KEY == "":
                    raise RuntimeError("TOTP_ENCRYPTION_KEY must be set in production")


settings = Settings()
