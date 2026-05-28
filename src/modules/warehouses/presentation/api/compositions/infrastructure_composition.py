"""This module contains composition functions for the warehouse module."""

from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from src.modules.warehouses.domain.ports.repositories.warehouse_repository_port import (
    WarehouserRepositoryPort,
)
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_cache_item_vo import (
    WarehouseCacheItemVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
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


def get_warehouse_by_supplier_cache_key_factory(
    data: dict[str, Any],
) -> WarehouseBySupplierCacheValueVO:
    """Factory function for WarehouseBySupplierCacheValueVO.

    Args:
        data (dict[str, Any]): The data to use to create the
            WarehouseBySupplierCacheValueVO instance.

    Returns:
        WarehouseBySupplierCacheValueVO: The WarehouseBySupplierCacheValueVO instance.
    """
    return WarehouseBySupplierCacheValueVO(
        warehouses=[
            WarehouseCacheItemVO(
                id=UUID(warehouse["id"]),
                supplier_id=UUID(warehouse["supplier_id"]),
                name=WarehouseNameVO(warehouse["name"]),
                address=WarehouseAddressVO(warehouse["address"]),
                is_active=warehouse["is_active"],
                created_at=warehouse["created_at"],
                updated_at=warehouse["updated_at"],
            )
            for warehouse in data["warehouses"]
        ]
    )


def get_warehouse_by_supplier_cache_outbound(
    redis_client: Redis = Depends(get_redis_client),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]:
    """Get the RedisCacheOutboundAdapter instance for the warehouse by supplier cache.

    Args:
        redis_client (Redis): The Redis client.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            outbound adapter.

    Returns:
        RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]: The RedisCacheOutboundAdapter
            instance.
    """
    return RedisCacheOutboundAdapter(
        redis_client=redis_client,
        factory=get_warehouse_by_supplier_cache_key_factory,
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


async def get_warehouse_repository(
    uow: SQLAlchemyWarehouseUnitOfWorkAdapter = Depends(get_warehouse_unit_of_work),
) -> WarehouserRepositoryPort:
    """Get the warehouse repository.

    Args:
        uow (SQLAlchemyWarehouseUnitOfWorkAdapter): The warehouse unit of work.

    Returns:
        WarehouserRepositoryPort: The warehouse repository.
    """
    return uow.warehouses
