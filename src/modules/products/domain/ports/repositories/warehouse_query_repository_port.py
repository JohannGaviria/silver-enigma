"""This module contains the WarehouseQueryRepositoryPort interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.value_objects.referenced_warehouse_vo import (
    ReferencedWarehouseVO,
)


class WarehouseQueryRepositoryPort(ABC):
    """Port for querying warehouse-related information.

    This port exposes read-only operations required by other modules
    to validate warehouse business rules without depending directly on
    the Warehouses module implementation.
    """

    @abstractmethod
    async def find_by_id(self, warehouse_id: UUID) -> ReferencedWarehouseVO | None:
        """Finds a WarehouseEntity by its ID.

        Args:
            warehouse_id (UUID): The ID of the warehouse to be found.

        Returns:
            ReferencedWarehouseVO | None: The found warehouse, or None if not found.
        """
        pass
