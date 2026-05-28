"""This module contains the WarehouseRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity


class WarehouserRepositoryPort(ABC):
    """Interface for a warehouse repository."""

    @abstractmethod
    async def find_all_by_supplier_id(self, supplier_id: UUID) -> list[WarehouseEntity]:
        """Find all warehouses by supplier ID.

        Args:
            supplier_id (UUID): The supplier ID to find warehouses for.

        Returns:
            list[WarehouseEntity]: A list of warehouse entities.
        """
        pass

    @abstractmethod
    async def save(self, entity: WarehouseEntity) -> WarehouseEntity:
        """Save a warehouse entity to the repository.

        Args:
            entity (WarehouseEntity): The warehouse entity to save.

        Returns:
            WarehouseEntity: The saved warehouse entity.
        """
        pass
