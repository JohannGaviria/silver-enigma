"""This module contains composition functions for the products module."""

from fastapi import Depends

from src.modules.products.application.use_cases.adjust_stock_use_case import (
    AdjustStockUseCase,
)
from src.modules.products.application.use_cases.create_product_use_case import (
    CreateProductUseCase,
)
from src.modules.products.application.use_cases.get_warehouse_stock_use_case import (
    GetWarehouseStockUseCase,
)
from src.modules.products.application.use_cases.toggle_product_status_use_case import (
    ToggleProductStatusUseCase,
)
from src.modules.products.application.use_cases.update_product_use_case import (
    UpdateProductUseCase,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_repository_adapter import (
    SQLAlchemyInventoryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_inventory_unit_of_work_adapter import (
    SQLAlchemyInventoryUnitOfWorkAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_unit_of_work_adapter import (
    SQLAlchemyProductUnitOfWorkAdapter,
)
from src.modules.products.presentation.api.compositions.infrastructure_composition import (
    get_inventory_repository,
    get_inventory_uow,
    get_product_uow,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
)


def get_create_product_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    product_unit_of_work: SQLAlchemyProductUnitOfWorkAdapter = Depends(get_product_uow),
) -> CreateProductUseCase:
    """Get the CreateProductUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        product_unit_of_work (SQLAlchemyProductUnitOfWorkAdapter): The product unit of work adapter.

    Returns:
        CreateProductUseCase: The CreateProductUseCase instance.
    """
    return CreateProductUseCase(
        logger_factory_outbound=logger_factory_outbound,
        product_unit_of_work=product_unit_of_work,
    )


def get_update_product_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    product_unit_of_work: SQLAlchemyProductUnitOfWorkAdapter = Depends(get_product_uow),
) -> UpdateProductUseCase:
    """Get the UpdateProductUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        product_unit_of_work (SQLAlchemyProductUnitOfWorkAdapter): The product unit of work adapter.

    Returns:
        UpdateProductUseCase: The UpdateProductUseCase instance.
    """
    return UpdateProductUseCase(
        logger_factory_outbound=logger_factory_outbound,
        product_unit_of_work=product_unit_of_work,
    )


def get_toggle_product_status_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    product_unit_of_work: SQLAlchemyProductUnitOfWorkAdapter = Depends(get_product_uow),
) -> ToggleProductStatusUseCase:
    """Get the ToggleProductStatusUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        product_unit_of_work (SQLAlchemyProductUnitOfWorkAdapter): The product unit of work adapter.

    Returns:
        ToggleProductStatusUseCase: The ToggleProductStatusUseCase instance.
    """
    return ToggleProductStatusUseCase(
        logger_factory_outbound=logger_factory_outbound,
        product_unit_of_work=product_unit_of_work,
    )


def get_adjust_stock_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    inventory_unit_of_work: SQLAlchemyInventoryUnitOfWorkAdapter = Depends(
        get_inventory_uow
    ),
) -> AdjustStockUseCase:
    """Get the AdjustStockUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        inventory_unit_of_work (SQLAlchemyInventoryUnitOfWorkAdapter): The inventory unit of work adapter.

    Returns:
        AdjustStockUseCase: The AdjustStockUseCase instance.
    """
    return AdjustStockUseCase(
        logger_factory_outbound=logger_factory_outbound,
        inventory_unit_of_work=inventory_unit_of_work,
    )


def get_get_warehouse_stock_use_case(
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    inventory_repository: SQLAlchemyInventoryRepositoryAdapter = Depends(
        get_inventory_repository
    ),
) -> GetWarehouseStockUseCase:
    """Get the GetWarehouseStockUseCase instance.

    Args:
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory outbound adapter.
        inventory_repository (SQLAlchemyInventoryRepositoryAdapter): The inventory repository adapter.

    Returns:
        GetWarehouseStockUseCase: The GetWarehouseStockUseCase instance.
    """
    return GetWarehouseStockUseCase(
        logger_factory_outbound=logger_factory_outbound,
        inventory_repository=inventory_repository,
    )
