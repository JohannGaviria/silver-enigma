"""This module contains the InventoryAllocationPersistenceMapper class."""

from src.modules.orders.domain.entities.inventory_allocation_entity import (
    InventoryAllocationEntity,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.infrastructure.persistence.models.inventory_allocation_model import (
    InventoryAllocationModel,
)


class InventoryAllocationPersistenceMapper:
    """Class responsible for mapping InventoryAllocation entities to and from SQLAlchemy models."""

    @staticmethod
    def to_entity(model: InventoryAllocationModel) -> InventoryAllocationEntity:
        """Map a SQLAlchemy model to an InventoryAllocation entity.

        Args:
            model (InventoryAllocationModel): The SQLAlchemy model to map.

        Returns:
            InventoryAllocationEntity: The mapped InventoryAllocation entity.
        """
        return InventoryAllocationEntity(
            id=model.id,
            order_item_id=model.order_item_id,
            warehouse_id=model.warehouse_id,
            quantity=QuantityVO(model.quantity),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: InventoryAllocationEntity) -> InventoryAllocationModel:
        """Map an InventoryAllocation entity to a SQLAlchemy model.

        Args:
            entity (InventoryAllocationEntity): The InventoryAllocation entity to map.

        Returns:
            InventoryAllocationModel: The mapped SQLAlchemy model.
        """
        return InventoryAllocationModel(
            id=entity.id,
            order_item_id=entity.order_item_id,
            warehouse_id=entity.warehouse_id,
            quantity=entity.quantity.value(),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
