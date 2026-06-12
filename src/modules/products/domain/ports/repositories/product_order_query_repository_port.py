"""This module contains the ProductOrderQueryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class ProductOrderQueryRepositoryPort(ABC):
    """Port for the product order query repository.

    This port exposes read-only operations required for the product
    to validate orders business rules without depending directly on
    the products module implementation.
    """

    @abstractmethod
    async def exists_by_product_id_and_statuses(
        self, product_id: UUID, statuses: set[OrderStatusEnum]
    ) -> bool:
        """Check if an order exists by product ID and statuses.

        Args:
            product_id (UUID): The ID of the product.
            statuses (set[OrderStatusEnum]): The set of statuses to check.

        Returns:
            bool: True if the order exists, False otherwise.
        """
        pass
