"""This module contains the ProductLifecycleUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.products.domain.ports.repositories.product_order_query_repository_port import (
    ProductOrderQueryRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class ProductLifecycleUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work scoped to the products and orders query module.

    Exposes the repositories that belong to the products and orders query
    bounded context so that application-layer use cases can access them
    through a single, transaction-aware entry point.

    Attributes:
        products (ProductOrderQueryRepositoryPort): Repository for product aggregate operations.
        orders_query (ProductOrderQueryRepositoryPort): Repository for order aggregate operations.
    """

    products: ProductOrderQueryRepositoryPort
    orders_query: ProductOrderQueryRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "ProductLifecycleUnitOfWorkPort":
        """Enter the product lifecycle unit of work context.

        Returns:
            ProductLifecycleUnitOfWorkPort: The instance of the ProductLifecycleUnitOfWorkPort.
        """
        pass
