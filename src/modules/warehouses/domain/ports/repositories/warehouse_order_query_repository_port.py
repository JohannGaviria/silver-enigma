"""This module contains the WarehouseOrderQueryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class WarehouseOrderQueryRepositoryPort(ABC):
    """Port for querying order information related to warehouses.

    This port exposes read-only operations required for the warehouses
    module to validate orders business rules without depending directly
    on the warehouses module implementation.
    """

    @abstractmethod
    async def exists_by_warehouse_id_and_statuses(
        self, warehouse_id: UUID, statuses: set[OrderStatusEnum]
    ) -> bool:
        """Check if an order exists for a warehouse with any of the given statuses.

        Args:
            warehouse_id (UUID): The ID of the warehouse.
            statuses (set[OrderStatusEnum]): The set of statuses to check.

        Returns:
            bool: True if a matching order exists, False otherwise.
        """
        pass
