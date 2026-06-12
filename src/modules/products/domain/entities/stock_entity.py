"""This module contains the StockEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.products.domain.exceptions.stock_exception import (
    StockConflictException,
)
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class StockEntity(BaseEntity):
    """Entity representing a stock item.

    Attributes:
        id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        total_stock (TotalStockVO): The total number of items in stock.
        reserved_stock (ReservedStockVO): The number of items reserved for purchase.
        created_at (datetime): The date and time the stock was created.
        updated_at (datetime): The date and time the stock was updated.
    """

    product_id: UUID
    warehouse_id: UUID
    total_stock: TotalStockVO
    reserved_stock: ReservedStockVO

    @classmethod
    def create(
        cls,
        product_id: UUID,
        warehouse_id: UUID,
        total_stock: TotalStockVO,
        reserved_stock: ReservedStockVO,
    ) -> "StockEntity":
        """Factory method to create a new StockEntity.

        This method creates a new StockEntity instance with the specified
        attributes. It sets the created_at and updated_at attributes to the
        current UTC datetime.

        Args:
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.
            total_stock (TotalStockVO): The total number of items in stock.
            reserved_stock (ReservedStockVO): The number of items reserved for purchase.

        Returns:
            StockEntity: A new StockEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            product_id=product_id,
            warehouse_id=warehouse_id,
            total_stock=total_stock,
            reserved_stock=reserved_stock,
            created_at=now,
            updated_at=now,
        )

    def update_total_stock(self, total_stock: TotalStockVO) -> "StockEntity":
        """Updates the total stock value.

        This method updates the total_stock attribute of the StockEntity
        instance with the provided value. It sets the updated_at attribute to
        the current UTC datetime.

        Args:
            total_stock (TotalStockVO): The new total stock value.

        Returns:
            StockEntity: The updated StockEntity instance.
        """
        if total_stock.value() < self.reserved_stock.value():
            raise StockConflictException(
                product_id=self.product_id,
                warehouse_id=self.warehouse_id,
                requested_quantity=total_stock.value(),
                reserved_stock=self.reserved_stock.value(),
            )

        now = datetime.now(UTC)
        return StockEntity(
            id=self.id,
            product_id=self.product_id,
            warehouse_id=self.warehouse_id,
            total_stock=total_stock,
            reserved_stock=self.reserved_stock,
            created_at=self.created_at,
            updated_at=now,
        )
