"""This module contains the InventoryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_stock_vo import ProductStockVO
from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)


class InventoryRepositoryPort(ABC):
    """Interface for the inventory repository port."""

    @abstractmethod
    async def find_all_products_and_stock(
        self,
        name: str | None,
        unit_of_measure: UnitOfMeasureEnum | None,
        page: int,
        page_size: int,
    ) -> ProductStockVO:
        """Finds all products and stock.

        Args:
            name (str | None): The name of the product to filter by.
            unit_of_measure (UnitOfMeasureEnum | None): The unit of measure of the product to filter by.
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            ProductStockVO: The product stock with pagination.
        """
        pass

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
