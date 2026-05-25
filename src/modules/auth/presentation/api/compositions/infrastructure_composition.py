"""This module contains composition functions for the auth module."""

from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from src.config import settings
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
from src.modules.auth.domain.value_objects.refresh_token_cache_value_vo import (
    RefreshTokenCacheValueVO,
)
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
    get_redis_client,
)


def get_password_hash_outbound() -> Argon2PasswordHashOutboundAdapter:
    """Get the Argon2PasswordHashOutboundAdapter instance.

    Returns:
        Argon2PasswordHashOutboundAdapter: The Argon2PasswordHashOutboundAdapter instance.
    """
    return Argon2PasswordHashOutboundAdapter(
        time_cost=settings.TIME_COST,
        memory_cost=settings.MEMORY_COST,
        parallelism=settings.PARALLELISM,
    )


def refresh_token_cache_value_factory(
    data: dict[str, Any],
) -> RefreshTokenCacheValueVO:
    """Factory function for RefreshTokenCacheValueVO.

    Args:
        data (dict[str, Any]): The data to use to create the RefreshTokenCacheValueVO instance.

    Returns:
        RefreshTokenCacheValueVO: The RefreshTokenCacheValueVO instance.
    """
    return RefreshTokenCacheValueVO(
        jti=UUID(data["jti"]),
        sub=UUID(data["sub"]),
        expires_in=data["expires_in"],
    )


def get_refresh_token_cache_outbound(
    redis_client: Redis = Depends(get_redis_client),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> RedisCacheOutboundAdapter[RefreshTokenCacheValueVO]:
    """Get a RedisCacheOutboundAdapter for the refresh token cache.

    Args:
        redis_client (Redis): The Redis client instance.
        factory (RefreshTokenCacheValueVO): The factory for creating cache values.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.

    Returns:
        RedisCacheOutboundAdapter[RefreshTokenCacheValueVO]: The RedisCacheOutboundAdapter
            instance.
    """
    return RedisCacheOutboundAdapter(
        redis_client=redis_client,
        factory=refresh_token_cache_value_factory,
        logger_factory_outbound=logger_factory_outbound,
    )


async def get_user_uow(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> AsyncGenerator[SQLAlchemyUserUnitOfWorkAdapter, None]:
    """Get an asynchronous SQLAlchemy user unit of work adapter.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.

    Returns:
        AsyncGenerator[SQLAlchemyUserUnitOfWorkAdapter, None]: An asynchronous SQLAlchemy
            user unit of work adapter.
    """
    session_factory = await DatabaseEngine.get_session_factory()
    async with SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    ) as uow:
        yield uow


async def get_user_repository(
    uow: SQLAlchemyUserUnitOfWorkAdapter = Depends(get_user_uow),
) -> UserRepositoryPort:
    """Get the SQLAlchemy user repository adapter.

    Args:
        uow (SQLAlchemyUserUnitOfWorkAdapter): The user unit of work.

    Returns:
        UserRepositoryPort: The user repository port.
    """
    return uow.users
