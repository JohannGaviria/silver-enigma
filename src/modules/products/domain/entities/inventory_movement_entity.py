"""This module contains the InventoryMovementEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.products.domain.enums.movement_type_log_enum import MovementTypeLogEnum
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class InventoryMovementEntity(BaseEntity):
    """Entity representing a movement of inventory.

    Attributes:
        product_id (UUID): The ID of the product associated with the movement.
        warehouse_id (UUID): The ID of the warehouse associated with the movement.
        order_id (UUID | None): The ID of the order associated with the movement.
        movement_type (MovementTypeLogEnum): The type of movement (reserve, release, decrement).
        quantity (int): The quantity of the product associated with the movement.
    """

    product_id: UUID
    warehouse_id: UUID
    order_id: UUID | None
    movement_type: MovementTypeLogEnum
    quantity: int

    @classmethod
    def create(
        cls,
        product_id: UUID,
        warehouse_id: UUID,
        movement_type: MovementTypeLogEnum,
        quantity: int,
        order_id: UUID | None = None,
    ) -> "InventoryMovementEntity":
        """Factory method to create a new InventoryMovementEntity instance.

        This method creates a new InventoryMovementEntity instance with the
        specified attributes. It sets the created_at and updated_at attributes
        to the current UTC datetime.

        Args:
            product_id (UUID): The ID of the product associated with the movement.
            warehouse_id (UUID): The ID of the warehouse associated with the movement.
            movement_type (MovementTypeLogEnum): The type of movement (reserve, release, decrement).
            quantity (int): The quantity of the product associated with the movement.
            order_id (UUID | None): The ID of the order associated with the movement.

        Returns:
            InventoryMovementEntity: A new InventoryMovementEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            product_id=product_id,
            warehouse_id=warehouse_id,
            order_id=order_id,
            movement_type=movement_type,
            quantity=quantity,
            created_at=now,
            updated_at=now,
        )
