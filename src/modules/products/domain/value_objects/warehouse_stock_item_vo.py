"""This module contains the WarehouseStockItemVO class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class WarehouseStockItemVO(BaseValueObject):
    """Value Object representing a warehouse stock item.

    Attributes:
        stock_id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier.
        name (ProductNameVO): The name of the product.
        total_stock (TotalStockVO): The total stock of the product.
        available_stock (AvailableStockVO): The available stock of the product.
        stock_disponible (int): The stock that is available for sale.
        created_at (datetime): The datetime when the warehouse stock item was created.
        updated_at (datetime): The datetime when the warehouse stock item was last updated.
    """

    stock_id: UUID
    product_id: UUID
    supplier_id: UUID
    name: ProductNameVO
    total_stock: TotalStockVO
    available_stock: AvailableStockVO
    stock_disponible: int
    created_at: datetime
    updated_at: datetime
