"""This module contains composition functions for the FastAPI application."""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.shared.infrastructure.cache.redis_connection import RedisConnection
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.outbound.pyjwt_token_outbound_adapter import (
    PyJWTTokenOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


def get_logger_factory_outbound() -> StructlogLoggerFactoryOutboundAdapter:
    """Get the StructlogLoggerFactoryOutboundAdapter instance.

    Returns:
        StructlogLoggerFactoryOutboundAdapter: The StructlogLoggerFactoryOutboundAdapter instance.
    """
    return StructlogLoggerFactoryOutboundAdapter()


async def get_redis_client() -> Redis:
    """Get a Redis client.

    Returns:
        Redis: A Redis client.
    """
    return await RedisConnection.get_client()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an asynchronous database session.

    Returns:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    session = await DatabaseEngine.create_session()

    try:
        yield session

    finally:
        await session.close()


def get_token_outbound() -> PyJWTTokenOutboundAdapter:
    """Get the PyJWTTokenOutboundAdapter instance.

    Returns:
        PyJWTTokenOutboundAdapter: The PyJWTTokenOutboundAdapter instance.
    """
    return PyJWTTokenOutboundAdapter(
        access_expires_in=settings.ACCESS_EXPIRES_IN,
        refresh_expires_in=settings.REFRESH_EXPIRES_IN,
        token_secret_key=settings.TOKEN_SECRET_KEY,
        token_algorithm=settings.TOKEN_ALGORITHM,
    )
