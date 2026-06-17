"""This module contains the OrderItemsRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity


class OrderItemsRepositoryPort(ABC):
    """Interface for managing order items entities."""

    @abstractmethod
    async def save_many(self, entities: list[OrderItemsEntity]) -> None:
        """Save multiple order items entities.

        Args:
            entities (list[OrderItemsEntity]): The order items entities to save.
        """
        pass
