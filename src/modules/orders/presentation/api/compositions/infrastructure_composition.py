"""This module contains the infrastructure composition for the Orders API."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from src.modules.orders.infrastructure.persistence.unit_of_work.sqlalchemy_order_management_unit_of_work_adapter import (
    SQLAlchemyOrderManagementUnitOfWorkAdapter,
)
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


async def get_order_management_uow(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
) -> AsyncGenerator[SQLAlchemyOrderManagementUnitOfWorkAdapter, None]:
    """Get an asynchronous SQLAlchemy order management unit of work adapter.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.

    Returns:
        AsyncGenerator[SQLAlchemyOrderManagementUnitOfWorkAdapter, None]: An asynchronous
            SQLAlchemy order management unit of work adapter.
    """
    session_factory = await DatabaseEngine.get_session_factory()
    async with SQLAlchemyOrderManagementUnitOfWorkAdapter(
        logger_factory_outbound=logger_factory_outbound,
        session_factory=session_factory,
    ) as uow:
        yield uow
