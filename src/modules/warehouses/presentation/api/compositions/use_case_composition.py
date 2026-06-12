"""This module contains the use case composition for the warehouse module."""

from fastapi import Depends

from src.modules.warehouses.application.use_cases.create_warehouse_use_case import (
    CreateWarehouseUseCase,
)
from src.modules.warehouses.application.use_cases.get_warehouses_use_case import (
    GetWarehousesUseCase,
)
from src.modules.warehouses.application.use_cases.toggle_warehouse_status_use_case import (
    ToggleWarehouseStatusUseCase,
)
from src.modules.warehouses.application.use_cases.update_warehouse_use_case import (
    UpdateWarehouseUseCase,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_lifecycle_unit_of_work_adapter import (
    SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
)
from src.modules.warehouses.presentation.api.compositions.infrastructure_composition import (
    get_warehouse_by_supplier_cache_outbound,
    get_warehouse_lifecycle_unit_of_work,
    get_warehouse_repository,
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
    cache_outbound: RedisCacheOutboundAdapter[
        WarehouseBySupplierCacheValueVO
    ] = Depends(get_warehouse_by_supplier_cache_outbound),
    warehouse_unit_of_work: SQLAlchemyWarehouseUnitOfWorkAdapter = Depends(
        get_warehouse_unit_of_work
    ),
) -> CreateWarehouseUseCase:
    """Get the CreateWarehouseUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger
            factory outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]):
            The cache outbound adapter.
        warehouse_unit_of_work (SQLAlchemyWarehouseUnitOfWorkAdapter): The warehouse
            unit of work adapter.

    Returns:
        CreateWarehouseUseCase: The CreateWarehouseUseCase instance.
    """
    return CreateWarehouseUseCase(
        logger_factory_outbound=logger_factory_outbound,
        cache_outbound=cache_outbound,
        warehouse_unit_of_work=warehouse_unit_of_work,
    )


def get_get_warehouses_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    cache_outbound: RedisCacheOutboundAdapter[
        WarehouseBySupplierCacheValueVO
    ] = Depends(get_warehouse_by_supplier_cache_outbound),
    warehouse_repository: SQLAlchemyWarehouseRepositoryAdapter = Depends(
        get_warehouse_repository
    ),
) -> GetWarehousesUseCase:
    """Get the GetWarehousesUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger
            factory outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]):
            The cache outbound adapter.
        warehouse_repository (SQLAlchemyWarehouseRepositoryAdapter): The warehouse
            repository adapter.

    Returns:
        GetWarehousesUseCase: The GetWarehousesUseCase instance.
    """
    return GetWarehousesUseCase(
        logger_factory_outbound=logger_factory_outbound,
        cache_outbound=cache_outbound,
        warehouse_repository=warehouse_repository,
    )


def get_update_warehouse_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    cache_outbound: RedisCacheOutboundAdapter[
        WarehouseBySupplierCacheValueVO
    ] = Depends(get_warehouse_by_supplier_cache_outbound),
    warehouse_unit_of_work: SQLAlchemyWarehouseUnitOfWorkAdapter = Depends(
        get_warehouse_unit_of_work
    ),
) -> UpdateWarehouseUseCase:
    """Get the UpdateWarehouseUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger
            factory outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]):
            The cache outbound adapter.
        warehouse_unit_of_work (SQLAlchemyWarehouseUnitOfWorkAdapter): The warehouse
            unit of work adapter.

    Returns:
        UpdateWarehouseUseCase: The UpdateWarehouseUseCase instance.
    """
    return UpdateWarehouseUseCase(
        logger_factory_outbound=logger_factory_outbound,
        cache_outbound=cache_outbound,
        warehouse_unit_of_work=warehouse_unit_of_work,
    )


def get_toggle_warehouse_status_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    cache_outbound: RedisCacheOutboundAdapter[
        WarehouseBySupplierCacheValueVO
    ] = Depends(get_warehouse_by_supplier_cache_outbound),
    warehouse_lifecycle_unit_of_work: SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter = Depends(
        get_warehouse_lifecycle_unit_of_work
    ),
) -> ToggleWarehouseStatusUseCase:
    """Get the ToggleWarehouseStatusUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger
            factory outbound adapter.
        cache_outbound (RedisCacheOutboundAdapter[WarehouseBySupplierCacheValueVO]):
            The cache outbound adapter.
        warehouse_lifecycle_unit_of_work (SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter): The warehouse
            lifecycle unit of work adapter.

    Returns:
        ToggleWarehouseStatusUseCase: The ToggleWarehouseStatusUseCase instance.
    """
    return ToggleWarehouseStatusUseCase(
        logger_factory_outbound=logger_factory_outbound,
        cache_outbound=cache_outbound,
        warehouse_lifecycle_unit_of_work=warehouse_lifecycle_unit_of_work,
    )
