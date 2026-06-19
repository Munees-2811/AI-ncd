"""Application settings loaded from environment variables (.env)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NCD Shield AI"
    environment: str = "development"

    # Security
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Database — prefer DATABASE_URL, otherwise assemble from parts.
    database_url: str = "sqlite:///./ncd_shield.db"

    # CORS
    frontend_origin: str = "http://localhost:3000"

    # Rate limiting
    rate_limit: str = "60/minute"

    # Default admin (seeded on startup)
    admin_email: str = "admin@ncdshield.ai"
    admin_password: str = "Admin@12345"

    # ML artifacts
    model_dir: str = "../ml/models"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
