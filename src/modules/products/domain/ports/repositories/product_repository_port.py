"""This module contains the ProductRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.entities.product_entity import ProductEntity


class ProductRepositoryPort(ABC):
    """Interface for the Product Repository, defining the contract for product-related data operations."""

    @abstractmethod
    async def find_by_id(self, product_id: UUID) -> ProductEntity | None:
        """Finds a ProductEntity by its ID.

        Args:
            product_id (UUID): The ID of the product to be found.

        Returns:
            ProductEntity | None: The found product entity, or None if not found.
        """
        pass

    @abstractmethod
    async def update(self, entity: ProductEntity) -> ProductEntity:
        """Updates a ProductEntity in the repository.

        Args:
            entity (ProductEntity): The product entity to be updated.

        Returns:
            ProductEntity: The updated product entity.
        """
        pass

    @abstractmethod
    async def save(self, entity: ProductEntity) -> ProductEntity:
        """Saves a ProductEntity to the repository.

        Args:
            entity (ProductEntity): The product entity to be saved.

        Returns:
            ProductEntity: The saved product entity.
        """
        pass
