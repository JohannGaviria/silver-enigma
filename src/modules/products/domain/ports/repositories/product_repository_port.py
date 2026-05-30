"""This module contains the ProductRepositoryPort class."""

from abc import ABC, abstractmethod

from src.modules.products.domain.entities.product_entity import ProductEntity


class ProductRepositoryPort(ABC):
    """Interface for the Product Repository, defining the contract for product-related data operations."""

    @abstractmethod
    async def save(self, entity: ProductEntity) -> ProductEntity:
        """Saves a ProductEntity to the repository.

        Args:
            entity (ProductEntity): The product entity to be saved.

        Returns:
            ProductEntity: The saved product entity.
        """
        pass
