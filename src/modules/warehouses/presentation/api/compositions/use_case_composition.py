"""This module contains the use case composition for the warehouse module."""

from fastapi import Depends

from src.modules.warehouses.application.use_cases.create_warehouse_use_case import (
    CreateWarehouseUseCase,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
)
from src.modules.warehouses.presentation.api.compositions.infrastructure_composition import (
    get_warehouse_by_supplier_cache_outbound,
    get_warehouse_unit_of_work,
)
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_create_warehouse_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    cache_outbound: RedisCacheOutboundAdapter = Depends(
        get_warehouse_by_supplier_cache_outbound
    ),
    warehouse_unit_of_work: SQLAlchemyWarehouseUnitOfWorkAdapter = Depends(
        get_warehouse_unit_of_work
    ),
) -> CreateWarehouseUseCase:
    """Get the CreateWarehouseUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter): The cache outbound adapter.
        warehouse_unit_of_work (SQLAlchemyWarehouseUnitOfWorkAdapter): The warehouse unit of work adapter.

    Returns:
        CreateWarehouseUseCase: The CreateWarehouseUseCase instance.
    """
    return CreateWarehouseUseCase(
        logger_factory_outbound=logger_factory_outbound,
        cache_outbound=cache_outbound,
        warehouse_unit_of_work=warehouse_unit_of_work,
    )
