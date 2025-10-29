from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret"
    JWT_ALGO: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "postgresql+psycopg2://app:app@localhost:5432/appdb"

    MAX_UPLOAD_MB: int = 100
    UPLOAD_DIR: str = "./storage/uploads"
    EXTRACT_DIR: str = "./storage/extracted"

    ENABLE_SSE: bool = True
    ENABLE_WS: bool = True

    # Langfuse
    LANGFUSE_HOST: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
