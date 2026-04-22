"""This module contains the application configuration settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application metadata
    APP_NAME: str = Field(..., validation_alias="APP_NAME")
    APP_SUMMARY: str = Field(..., validation_alias="APP_SUMMARY")
    APP_DESCRIPTION: str = Field(..., validation_alias="APP_DESCRIPTION")

    # Backend configuration
    DEBUG: bool = Field(..., validation_alias="DEBUG")
    ENVIRONMENT: str = Field(..., validation_alias="ENVIRONMENT")
    BACKEND_PORT: int = Field(..., validation_alias="BACKEND_PORT")
    BACKEND_WORKERS: int = Field(..., validation_alias="BACKEND_WORKERS")
    CORS_ALLOW_ORIGINS: str = Field(..., validation_alias="CORS_ALLOW_ORIGINS")
    CORS_ALLOW_CREDENTIALS: str = Field(..., validation_alias="CORS_ALLOW_CREDENTIALS")

    # Database configuration
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    DB_PORT: int = Field(..., validation_alias="DB_PORT")
    POSTGRES_USER: str = Field(..., validation_alias="POSTGRES_USER")
    POSTGRES_DB: str = Field(..., validation_alias="POSTGRES_DB")
    POSTGRES_PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")

    # Redis configuration
    REDIS_PORT: int = Field(..., validation_alias="REDIS_PORT")
    REDIS_PASSWORD: str = Field(..., validation_alias="REDIS_PASSWORD")
    REDIS_HOST: str = Field(..., validation_alias="REDIS_HOST")
    REDIS_DB: int = Field(..., validation_alias="REDIS_DB")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: The application settings instance.
    """
    settings = Settings()  # type: ignore[call-arg]
    return settings


settings = get_settings()
