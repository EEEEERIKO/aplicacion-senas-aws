from pydantic import BaseSettings
import os
import secrets


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    # SECURITY: SECRET_KEY must be set via environment variable in production
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
