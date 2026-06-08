"""This module contains the InventoryUnitOfWorkPort class."""

from abc import abstractmethod

from src.modules.products.domain.ports.repositories.inventory_movement_repository_port import (
    InventoryMovementRepositoryPort,
)
from src.modules.products.domain.ports.repositories.product_repository_port import (
    ProductRepositoryPort,
)
from src.modules.products.domain.ports.repositories.stock_repository_port import (
    StockRepositoryPort,
)
from src.modules.products.domain.ports.repositories.warehouse_query_repository_port import (
    WarehouseQueryRepositoryPort,
)
from src.shared.domain.ports.unit_of_work.unit_of_work_port import UnitOfWorkPort


class InventoryUnitOfWorkPort(UnitOfWorkPort):
    """Unit of work for inventory-related operations.

    Coordinates all repositories required to execute inventory business
    operations atomically within a single transaction.

    This unit of work is intended for use cases that need to interact
    with products, stocks, and warehouse information while ensuring
    transactional consistency.

    Attributes:
        stocks (StockRepositoryPort): Repository used to manage stock records.
        products (ProductRepositoryPort): Repository used to access product data.
        warehouses (WarehouseQueryRepositoryPort): Repository used to query
            warehouse-related information required by inventory validations.
        inventory_movements (InventoryMovementRepositoryPort): Repository used
            to manage inventory movement records.
    """

    stocks: StockRepositoryPort
    products: ProductRepositoryPort
    warehouses: WarehouseQueryRepositoryPort
    inventory_movements: InventoryMovementRepositoryPort

    @abstractmethod
    async def __aenter__(self) -> "InventoryUnitOfWorkPort":
        """Enter the inventory unit of work context.

        Returns:
            InventoryUnitOfWorkPort: The inventory unit of work context.
        """
        pass
