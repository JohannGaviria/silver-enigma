"""This module contains the InventoryMovementPersistenceMapper class."""

from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)
from src.modules.products.infrastructure.persistence.models.inventory_movement_model import (
    InventoryMovementModel,
)


class InventoryMovementPersistenceMapper:
    """Mapper for InventoryMovementModel to InventoryMovementEntity."""

    @staticmethod
    def to_model(entity: InventoryMovementEntity) -> InventoryMovementModel:
        """Map an InventoryMovementEntity to an InventoryMovementModel.

        Args:
            entity (InventoryMovementEntity): The InventoryMovementEntity to be mapped.

        Returns:
            InventoryMovementModel: The mapped InventoryMovementModel.
        """
        return InventoryMovementModel(
            id=entity.id,
            product_id=entity.product_id,
            warehouse_id=entity.warehouse_id,
            order_id=entity.order_id,
            movement_type=entity.movement_type,
            quantity=entity.quantity,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
