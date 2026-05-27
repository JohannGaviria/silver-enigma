"""This module contains composition functions for the warehouse module."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis

from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
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


def get_warehouse_by_supplier_cache_outbound(
    redis_client: Redis = Depends(get_redis_client),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> RedisCacheOutboundAdapter:
    """Get the RedisCacheOutboundAdapter instance for the warehouse by supplier cache.

    Args:
        redis_client (Redis): The Redis client.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            outbound adapter.

    Returns:
        RedisCacheOutboundAdapter: The RedisCacheOutboundAdapter instance.
    """
    return RedisCacheOutboundAdapter(
        redis_client=redis_client,
        factory=None,  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


async def get_warehouse_unit_of_work(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> AsyncGenerator[SQLAlchemyWarehouseUnitOfWorkAdapter, None]:
    """Get an asynchronous warehouse unit of work.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            outbound adapter.

    Returns:
        AsyncGenerator[SQLAlchemyWarehouseUnitOfWorkAdapter, None]: An asynchronous
            warehouse unit of work.
    """
    session_factory = await DatabaseEngine.get_session_factory()
    async with SQLAlchemyWarehouseUnitOfWorkAdapter(
        session_factory=session_factory, logger_factory_outbound=logger_factory_outbound
    ) as uow:
        yield uow
