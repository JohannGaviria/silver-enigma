"""This module contains the OrderStatusHistoryRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)


class OrderStatusHistoryRepositoryPort(ABC):
    """Interface for managing order status history entities."""

    @abstractmethod
    async def save(self, entity: OrderStatusHistoryEntity) -> None:
        """Save an order status history entity.

        Args:
            entity (OrderStatusHistoryEntity): The order status history entity to save.
        """
        pass
