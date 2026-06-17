"""This module contains the ProductQueryRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.orders.domain.value_object.referenced_product_vo import (
    ReferencedProductVO,
)


class ProductQueryRepositoryPort(ABC):
    """Interface for querying product data.

    This port exposes read-only operations required for the order
    to validate products business rules without depending directly
    on the orders module implementation.
    """

    @abstractmethod
    async def find_by_ids(self, product_ids: list[UUID]) -> list[ReferencedProductVO]:
        """Find products by IDs.

        Args:
            product_ids (list[UUID]): A list of product IDs.

        Returns:
            list[ReferencedProductVO]: A list of product details.
        """
        pass
