"""This module contains the InventoryAllocationEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class InventoryAllocationEntity(BaseEntity):
    """Entity representing the fulfillment allocation of an order item to a warehouse.

    An inventory allocation records that a given quantity of an order item
    will be (or was) fulfilled from a specific warehouse. An order item may
    be split across multiple allocations if it is fulfilled from more than
    one warehouse (see ADR-013).

    Attributes:
        order_item_id (UUID): The ID of the order item being allocated.
        warehouse_id (UUID): The ID of the warehouse fulfilling this allocation.
        quantity (QuantityVO): The quantity allocated from this warehouse.
        created_at (datetime): The timestamp when the allocation was created.
        updated_at (datetime): The timestamp when the allocation was last updated.
    """

    order_item_id: UUID
    warehouse_id: UUID
    quantity: QuantityVO

    @classmethod
    def create(
        cls,
        order_item_id: UUID,
        warehouse_id: UUID,
        quantity: QuantityVO,
    ) -> "InventoryAllocationEntity":
        """Factory method to create a new InventoryAllocationEntity instance.

        Args:
            order_item_id (UUID): The ID of the order item being allocated.
            warehouse_id (UUID): The ID of the warehouse fulfilling this allocation.
            quantity (QuantityVO): The quantity allocated from this warehouse.

        Returns:
            InventoryAllocationEntity: A new InventoryAllocationEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            order_item_id=order_item_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            created_at=now,
            updated_at=now,
        )
