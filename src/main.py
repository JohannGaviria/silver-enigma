"""This module contains the main application code for the FastAPI application."""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.shared.infrastructure.cache.redis_connection import RedisConnection
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.logging.structlog_configure_logging import (
    StructlogConfigureLogging,
)

app = FastAPI(
    title=settings.APP_NAME,
    summary=settings.APP_SUMMARY,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
)

# Configure logging using Structlog
StructlogConfigureLogging.configure(debug=settings.DEBUG)


@app.get(
    path="/",
    tags=["System"],
    summary="Root Endpoint",
    description="Returns a welcome message.",
)
async def root() -> JSONResponse:
    """Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return JSONResponse(
        content={"message": f"Welcome to the {settings.APP_NAME}!"},
        status_code=status.HTTP_200_OK,
    )


@app.get(
    path="/health",
    tags=["System"],
    summary="Health Check Endpoint",
    description="Checks the operational status of the server, PostgreSQL, and Redis.",
)
async def health_check() -> JSONResponse:
    """Health check endpoint that verifies the status of the server, PostgreSQL, and Redis.

    Returns:
        dict: A dictionary containing the health status of the services.
    """
    db_status = DatabaseEngine.health_check()
    redis_status = RedisConnection.health_check()

    if db_status and redis_status:
        return JSONResponse(
            content={
                "status": "healthy",
                "database": db_status,
                "redis": redis_status,
            },
            status_code=status.HTTP_200_OK,
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "status": "unhealthy",
            "database": db_status,
            "redis": redis_status,
        },
    )
