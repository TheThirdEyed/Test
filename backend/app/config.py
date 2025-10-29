
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "multiagent-docs"
    ENV: str = "dev"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str | None = None
    ALLOW_ORIGINS: List[AnyHttpUrl] | List[str] = ["http://localhost:5173", "http://localhost:4321", "*"]
    MAX_UPLOAD_MB: int = 100

    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_DEPLOYMENT: str | None = None

    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _db_from_env(cls, v):
        return v or os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/madocs")

settings = Settings()  # type: ignore
