"""This module contains the WarehouseUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.warehouses.domain.ports.repositories.warehouse_repository_port import (
    WarehouserRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class WarehouseUnitOfWorkPort(UnitOfWorkPort):
    """Unit of Work scoped to the warehouses module.

    Exposes the repositories that belong to the warehouses bounded context so
    that application-layer use cases can access them through a single,
    transaction-aware entry point.

    Attributes:
        warehouses (WarehouseRepositoryPort): Repository for warehouse aggregate operations.
    """

    warehouses: WarehouserRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "WarehouseUnitOfWorkPort":
        """Enter the warehouse unit of work context.

        Returns:
            WarehouseUnitOfWorkPort: This instance, ready to use.
        """
        pass
