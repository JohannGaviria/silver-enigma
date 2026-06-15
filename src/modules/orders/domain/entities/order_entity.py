"""This module contains the OrderEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


@dataclass(frozen=True)
class OrderEntity(BaseEntity):
    """Entity representing an order.

    Attributes:
        buyer_id (UUID): The ID of the buyer.
        supplier_id (UUID): The ID of the supplier.
        warehouse_id (UUID): The ID of the warehouse.
        status_order (OrderStatusEnum): The order status.
    """

    buyer_id: UUID
    supplier_id: UUID
    warehouse_id: UUID
    status_order: OrderStatusEnum

    @classmethod
    def create(
        cls,
        buyer_id: UUID,
        supplier_id: UUID,
        warehouse_id: UUID,
        status_order: OrderStatusEnum,
    ) -> "OrderEntity":
        """Factory method to create a new OrderEntity instance.

        Args:
            buyer_id (UUID): The ID of the buyer.
            supplier_id (UUID): The ID of the supplier.
            warehouse_id (UUID): The ID of the warehouse.
            status_order (OrderStatusEnum): The order status.

        Returns:
            OrderEntity: A new OrderEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            status_order=status_order,
            created_at=now,
            updated_at=now,
        )
