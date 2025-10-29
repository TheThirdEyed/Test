
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "multiagent-docs"
    ENV: str = "dev"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str | None = None
    ALLOW_ORIGINS: List[str] = ["http://localhost:5173", "*"]
    MAX_UPLOAD_MB: int = 100

    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None

    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _db_from_env(cls, v):
        return v or os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/madocs")

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

settings = Settings()  # type: ignore
