"""This module contains the GetWarehouseStockSchema class."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WarehouseStockItemSchema(BaseModel):
    """Schema representing a warehouse stock item.

    Attributes:
        stock_id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        name (str): The name of the product.
        total_stock (int): The total stock of the product.
        available_stock (int): The available stock of the product.
        stock_disponible (int): The stock that is available for sale.
        created_at (datetime): The datetime when the warehouse stock item was created.
        updated_at (datetime): The datetime when the warehouse stock item was last updated.
    """

    stock_id: UUID
    product_id: UUID
    name: str
    total_stock: int
    available_stock: int
    stock_disponible: int
    created_at: datetime
    updated_at: datetime


class GetWarehouseStockResponseSchema(BaseModel):
    """Schema representing the response for get warehouse stock.

    Attributes:
        warehouse_stock (list[WarehouseStockItemSchema]): A list of warehouse stock items.
    """

    warehouse_stock: list[WarehouseStockItemSchema]
