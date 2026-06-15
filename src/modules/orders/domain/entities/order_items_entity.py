"""This module contains the OrderItemsEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.modules.orders.domain.value_object.quantity_vo import QuantityVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class OrderItemsEntity(BaseEntity):
    """Entity representing an order item.

    Attributes:
        id (UUID): The unique identifier of the order item.
        order_id (UUID): The ID of the order.
        product_id (UUID): The ID of the product.
        quantity (int): The quantity of the product.
        unit_price (Decimal): The unit price of the product.
        created_at (datetime): The timestamp when the order item was created.
        updated_at (datetime): The timestamp when the order item was last updated.
    """

    order_id: UUID
    product_id: UUID
    quantity: QuantityVO
    unit_price: Decimal

    @classmethod
    def create(
        cls,
        order_id: UUID,
        product_id: UUID,
        quantity: QuantityVO,
        unit_price: Decimal,
    ) -> "OrderItemsEntity":
        """Factory method to create a new OrderItemsEntity instance.

        Args:
            order_id (UUID): The ID of the order.
            product_id (UUID): The ID of the product.
            quantity (QuantityVO): The quantity of the product.
            unit_price (Decimal): The unit price of the product.

        Returns:
            OrderItemsEntity: A new OrderItemsEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            created_at=now,
            updated_at=now,
        )
