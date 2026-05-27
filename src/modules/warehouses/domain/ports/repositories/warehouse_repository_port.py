"""This module contains the WarehouseRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity


class WarehouserRepositoryPort(ABC):
    """Interface for a warehouse repository."""

    @abstractmethod
    async def save(self, entity: WarehouseEntity) -> WarehouseEntity:
        """Save a warehouse entity to the repository.

        Args:
            entity (WarehouseEntity): The warehouse entity to save.

        Returns:
            WarehouseEntity: The saved warehouse entity.
        """
        pass
