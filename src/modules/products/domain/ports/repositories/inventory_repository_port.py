"""This module contains the InventoryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)


class InventoryRepositoryPort(ABC):
    """Interface for the inventory repository port."""

    @abstractmethod
    async def find_inventory_by_user_and_warehouse(
        self, user_id: UUID, warehouse_id: UUID, page: int, page_size: int
    ) -> WarehouseStockVO:
        """Finds the inventory by user and warehouse.

        Args:
            user_id (UUID): The ID of the user.
            warehouse_id (UUID): The ID of the warehouse.
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            WarehouseStockVO: The warehouse stock.
        """
        pass
