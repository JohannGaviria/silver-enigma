"""This module contains the InventoryAllocationRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.orders.domain.entities.inventory_allocation_entity import (
    InventoryAllocationEntity,
)


class InventoryAllocationRepositoryPort(ABC):
    """Interface for managing inventory allocation entities.

    Inventory allocations record which warehouse(s) fulfill a given order
    item. This port is currently unused by any use case — fulfillment is
    not yet implemented — but is defined now so that the persisted model
    has a corresponding domain-facing repository contract, consistent with
    every other entity in this module.
    """

    @abstractmethod
    async def save_many(self, entities: list[InventoryAllocationEntity]) -> None:
        """Save multiple inventory allocation entities.

        Args:
            entities (list[InventoryAllocationEntity]): The inventory allocation entities to save.
        """
        pass
