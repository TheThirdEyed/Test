
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os, json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    APP_NAME: str = "multiagent-docs"
    ENV: str = "dev"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    DATABASE_URL: Optional[str] = None
    ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "*"])
    MAX_UPLOAD_MB: int = 100

    # LLM providers
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    OPENAI_EMBED_MODEL: Optional[str] = None

    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _db_from_env(cls, v):
        return v or os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/madocs")

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def _parse_allow_origins(cls, v):
        if v is None:
            return ["http://localhost:5173"]
        if isinstance(v, list):
            return [str(x).strip() for x in v]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                try:
                    arr = json.loads(s)
                    if isinstance(arr, list):
                        return [str(x).strip() for x in arr]
                except Exception:
                    pass
            return [p.strip() for p in s.split(",") if p.strip()]
        return [str(v).strip()]

settings = Settings()  # type: ignore
