"""This module contains the WarehouseLifecycleUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.warehouses.domain.ports.repositories.warehouse_order_query_repository_port import (
    WarehouseOrderQueryRepositoryPort,
)
from src.modules.warehouses.domain.ports.repositories.warehouse_repository_port import (
    WarehouserRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class WarehouseLifecycleUnitOfWorkPort(UnitOfWorkPort):
    """Unit of Work scoped to the warehouses and orders query modules.

    Exposes the repositories that belong to the warehouses and orders query
    bounded context so that application-layer use cases can access them
    through a single, transaction-aware entry point.

    Attributes:
        warehouses (WarehouseRepositoryPort): Repository for warehouse aggregate operations.
        orders_query (WarehouseOrderQueryRepositoryPort): Repository for warehouse order query operations.
    """

    warehouses: WarehouserRepositoryPort
    orders_query: WarehouseOrderQueryRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "WarehouseLifecycleUnitOfWorkPort":
        """Enter the warehouse lifecycle unit of work context.

        Returns:
            WarehouseLifecycleUnitOfWorkPort: This instance, ready to use.
        """
        pass
