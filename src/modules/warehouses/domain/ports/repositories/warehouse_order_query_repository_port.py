"""This module contains the OrderQueryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.warehouses.domain.value_objects.warehouse_referenced_order_vo import (
    WarehouseReferencedOrderVO,
)


class WarehouseOrderQueryRepositoryPort(ABC):
    """Port for the warehouse order query repository.

    This port exposes read-only operations required for the warehouse
    to validate orders business rules without depending directly on
    the warehouses module implementation.
    """

    @abstractmethod
    async def find_by_warehouse_id(
        self, warehouse_id: UUID
    ) -> WarehouseReferencedOrderVO | None:
        """Find a referenced order by warehouse ID.

        Args:
            warehouse_id (UUID): The ID of the warehouse.

        Returns:
            WarehouseReferencedOrderVO | None: The referenced order or None if not found.
        """
        pass
