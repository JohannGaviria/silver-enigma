"""This module contains the ProductUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.products.domain.ports.repositories.product_repository_port import (
    ProductRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class ProductUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work scoped to the product module.

    Exposes the repositories that belong to the products bounded context so
    that application-layer use cases can access them through a single,
    transaction-aware entry point.

    Attributes:
        products (ProductRepositoryPort): Repository for product aggregate operations.
    """

    products: ProductRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "ProductUnitOfWorkPort":
        """Enter the product unit of work context.

        Returns:
            ProductUnitOfWorkPort: The instance of the ProductUnitOfWorkPort.
        """
        pass
