from pydantic import BaseSettings
import os
import secrets


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"

    # DynamoDB
    DYNAMO_TABLE_NAME: str = os.environ.get("DYNAMO_TABLE", "aplicacion-senas-content")
    DYNAMO_ENDPOINT_URL: str | None = os.environ.get("DYNAMO_ENDPOINT_URL")  # For local testing
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")

    # S3
    S3_BUCKET: str = os.environ.get("S3_BUCKET", "aplicacion-senas-assets")
    S3_ENDPOINT_URL: str | None = os.environ.get("S3_ENDPOINT_URL")  # For local testing

    # AWS Credentials (for local testing only)
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")

    # Security
    # SECURITY: SECRET_KEY must be set via environment variable in production
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # CORS - Configure allowed origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative dev server
        "http://127.0.0.1:3000",
        # Add production domains here
    ]

    # Environment
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"


settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings