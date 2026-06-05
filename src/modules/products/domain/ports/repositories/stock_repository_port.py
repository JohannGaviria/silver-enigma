"""This module contains the StockRepositoryPort class."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.modules.products.domain.entities.stock_entity import StockEntity


class StockRepositoryPort(ABC):
    """Interface for the Stock Repository, defining the contract for stock-related data operations."""

    @abstractmethod
    async def find_by_id(self, stock_id: UUID) -> StockEntity | None:
        """Finds a StockEntity by its ID.

        Args:
            stock_id (UUID): The ID of the stock to be found.

        Returns:
            StockEntity | None: The found stock entity, or None if not found.
        """
        pass

    @abstractmethod
    async def find_by_product_and_warehouse(
        self, product_id: UUID, warehouse_id: UUID
    ) -> StockEntity | None:
        """Finds a StockEntity by its product and warehouse IDs.

        Args:
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.

        Returns:
            StockEntity | None: The found stock entity, or None if not found.
        """
        pass

    @abstractmethod
    async def update(self, entity: StockEntity) -> StockEntity:
        """Updates a StockEntity in the repository.

        Args:
            entity (StockEntity): The stock entity to be updated.

        Returns:
            StockEntity: The updated stock entity.
        """
        pass

    @abstractmethod
    async def save(self, entity: StockEntity) -> StockEntity:
        """Saves a StockEntity to the repository.

        Args:
            entity (StockEntity): The stock entity to be saved.

        Returns:
            StockEntity: The saved stock entity.
        """
        pass
