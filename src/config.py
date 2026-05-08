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
    CORS_ALLOW_CREDENTIALS: bool = Field(..., validation_alias="CORS_ALLOW_CREDENTIALS")
    FIRST_ADMIN_NAME: str = Field(..., validation_alias="FIRST_ADMIN_NAME")
    FIRST_ADMIN_EMAIL: str = Field(..., validation_alias="FIRST_ADMIN_EMAIL")
    FIRST_ADMIN_PASSWORD: str = Field(..., validation_alias="FIRST_ADMIN_PASSWORD")

    # Password hashing configuration
    TIME_COST: int = Field(..., validation_alias="TIME_COST")
    MEMORY_COST: int = Field(..., validation_alias="MEMORY_COST")
    PARALLELISM: int = Field(..., validation_alias="PARALLELISM")

    # Token configuration
    ACCESS_EXPIRES_IN: int = Field(..., validation_alias="ACCESS_EXPIRES_IN")
    REFRESH_EXPIRES_IN: int = Field(..., validation_alias="REFRESH_EXPIRES_IN")
    TOKEN_SECRET_KEY: str = Field(..., validation_alias="TOKEN_SECRET_KEY")
    TOKEN_ALGORITHM: str = Field(..., validation_alias="TOKEN_ALGORITHM")

    # Database configuration
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    DATABASE_URL_ALEMBIC: str = Field(..., validation_alias="DATABASE_URL_ALEMBIC")
    DB_HOST: str = Field(..., validation_alias="DB_HOST")
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
