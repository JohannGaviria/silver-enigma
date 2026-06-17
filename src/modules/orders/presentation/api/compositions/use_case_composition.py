"""This module contains the use case composition for the Orders API."""

from fastapi import Depends

from src.modules.orders.application.use_cases.create_order_use_case import (
    CreateOrderUseCase,
)
from src.modules.orders.infrastructure.persistence.unit_of_work.sqlalchemy_order_management_unit_of_work_adapter import (
    SQLAlchemyOrderManagementUnitOfWorkAdapter,
)
from src.modules.orders.presentation.api.compositions.infrastructure_composition import (
    get_order_management_uow,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_create_order_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    order_management_uow: SQLAlchemyOrderManagementUnitOfWorkAdapter = Depends(
        get_order_management_uow
    ),
) -> CreateOrderUseCase:
    """Get the CreateOrderUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory
            for creating loggers.
        order_management_uow (SQLAlchemyOrderManagementUnitOfWorkAdapter): The order management
            unit of work.

    Returns:
        CreateOrderUseCase: The CreateOrderUseCase instance.
    """
    return CreateOrderUseCase(
        logger_factory_outbound=logger_factory_outbound,
        order_management_unit_of_work=order_management_uow,
    )
