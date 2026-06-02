"""This module contains the StockEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class StockEntity(BaseEntity):
    """Entity representing a stock item.

    Attributes:
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        total_stock (int): The total number of items in stock.
        available_stock (int): The number of items available for purchase.
    """

    product_id: UUID
    warehouse_id: UUID
    total_stock: TotalStockVO
    available_stock: AvailableStockVO

    @classmethod
    def create(
        cls,
        product_id: UUID,
        warehouse_id: UUID,
        total_stock: TotalStockVO,
        available_stock: AvailableStockVO,
    ) -> "StockEntity":
        """Factory method to create a new StockEntity.

        This method creates a new StockEntity instance with the specified
        attributes. It sets the created_at and updated_at attributes to the
        current UTC datetime.

        Args:
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.
            total_stock (TotalStockVO): The total number of items in stock.
            available_stock (AvailableStockVO): The number of items available for purchase.

        Returns:
            StockEntity: A new StockEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=total_stock,
            available_stock=available_stock,
            created_at=now,
            updated_at=now,
        )
