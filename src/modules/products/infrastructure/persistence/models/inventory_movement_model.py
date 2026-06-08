"""This module contains the InventoryMovementModel class."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class InventoryMovementModel(BaseModel):
    """Model representing a movement of inventory.

    Attributes:
        id (UUID): The ID of the movement.
        product_id (UUID): The ID of the product associated with the movement.
        warehouse_id (UUID): The ID of the warehouse associated with the movement.
        order_id (UUID | None): The ID of the order associated with the movement.
        movement_type (str): The type of movement (reserve, release, decrement).
        quantity (int): The quantity of the product associated with the movement.
        created_at (datetime): The date and time the movement was created.
        updated_at (datetime): The date and time the movement was updated.
    """

    __tablename__ = "inventory_movements"

    product_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    order_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    movement_type: Mapped[str] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
