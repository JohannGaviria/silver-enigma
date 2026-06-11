"""This module contains the WarehouseStockItemVO class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO


@dataclass(frozen=True)
class WarehouseStockItemVO:
    """Value Object representing a warehouse stock item.

    Attributes:
        stock_id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier.
        name (ProductNameVO): The name of the product.
        total_stock (TotalStockVO): The total stock of the product.
        reserved_stock (ReservedStockVO): The reserved stock of the product.
        stock_disponible (int): The stock that is available for sale.
        created_at (datetime): The datetime when the warehouse stock item was created.
        updated_at (datetime): The datetime when the warehouse stock item was last updated.
    """

    stock_id: UUID
    product_id: UUID
    supplier_id: UUID
    name: ProductNameVO
    total_stock: TotalStockVO
    reserved_stock: ReservedStockVO
    stock_disponible: int
    created_at: datetime
    updated_at: datetime
