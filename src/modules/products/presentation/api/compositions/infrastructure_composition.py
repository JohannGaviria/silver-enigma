"""This module contains composition functions for the products module."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_inventory_unit_of_work_adapter import (
    SQLAlchemyInventoryUnitOfWorkAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_unit_of_work_adapter import (
    SQLAlchemyProductUnitOfWorkAdapter,
)
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


async def get_product_uow(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> AsyncGenerator[SQLAlchemyProductUnitOfWorkAdapter, None]:
    """Get the SQLAlchemyProductUnitOfWorkAdapter instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory for creating loggers.

    Returns:
        SQLAlchemyProductUnitOfWorkAdapter: The SQLAlchemyProductUnitOfWorkAdapter instance.
    """
    session_factory = await DatabaseEngine.get_session_factory()
    async with SQLAlchemyProductUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    ) as uow:
        yield uow


async def get_inventory_uow(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> AsyncGenerator[SQLAlchemyInventoryUnitOfWorkAdapter, None]:
    """Get the SQLAlchemyInventoryUnitOfWorkAdapter instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory for creating loggers.

    Returns:
        SQLAlchemyInventoryUnitOfWorkAdapter: The SQLAlchemyInventoryUnitOfWorkAdapter instance.
    """
    session_factory = await DatabaseEngine.get_session_factory()
    async with SQLAlchemyInventoryUnitOfWorkAdapter(
        session_factory=session_factory,
        logger_factory_outbound=logger_factory_outbound,
    ) as uow:
        yield uow
