"""This module contains the InventoryMovementRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)


class InventoryMovementRepositoryPort(ABC):
    """Interface for the InventoryMovementRepository.

    defining the contract for inventory movement-related data operations.
    """

    @abstractmethod
    async def save(self, entity: InventoryMovementEntity) -> None:
        """Saves the InventoryMovementEntity to the repository.

        Args:
            entity (InventoryMovementEntity): The InventoryMovementEntity to be saved.

        Returns:
            None
        """
        pass
