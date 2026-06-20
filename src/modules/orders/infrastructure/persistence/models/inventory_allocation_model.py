"""This module contains the InventoryAllocationModel class."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class InventoryAllocationModel(BaseModel):
    """Model representing an inventory allocation.

    Records that a given quantity of an order item is fulfilled from a
    specific warehouse. An order item may have multiple allocation rows
    if it is split across warehouses.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the inventory allocation.
        order_item_id (Mapped[UUID]): The ID of the order item being allocated.
        warehouse_id (Mapped[UUID]): The ID of the warehouse fulfilling this allocation.
        quantity (Mapped[int]): The quantity allocated from this warehouse.
        created_at (Mapped[datetime]): The timestamp when the allocation was created.
        updated_at (Mapped[datetime]): The timestamp when the allocation was last updated.
    """

    __tablename__ = "inventory_allocations"
    order_item_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
