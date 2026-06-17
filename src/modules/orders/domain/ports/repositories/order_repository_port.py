"""This module contains the OrderRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.orders.domain.entities.order_entity import OrderEntity


class OrderRepositoryPort(ABC):
    """Interface for managing order entities."""

    @abstractmethod
    async def save(self, entity: OrderEntity) -> OrderEntity:
        """Save an order entity.

        Args:
            entity (OrderEntity): The order entity to save.

        Returns:
            OrderEntity: The saved order entity.
        """
        pass
