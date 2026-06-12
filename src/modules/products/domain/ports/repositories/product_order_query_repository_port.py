"""This module contains the ProductOrderQueryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.value_objects.product_referenced_order_vo import (
    ProductReferencedOrderVO,
)


class ProductOrderQueryRepositoryPort(ABC):
    """Port for the product order query repository.

    This port exposes read-only operations required for the product
    to validate orders business rules without depending directly on
    the products module implementation.
    """

    @abstractmethod
    async def find_order_by_product_id(
        self, product_id: UUID
    ) -> ProductReferencedOrderVO | None:
        """Finds an order by product ID.

        Args:
            product_id (UUID): The ID of the product.

        Returns:
            ProductReferencedOrderVO | None: The product referenced order, or None if not found.
        """
        pass
