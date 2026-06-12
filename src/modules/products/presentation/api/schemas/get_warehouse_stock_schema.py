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
        reserved_stock (int): The reserved stock of the product.
        available_stock (int): The stock that is available for sale.
        created_at (datetime): The datetime when the warehouse stock item was created.
        updated_at (datetime): The datetime when the warehouse stock item was last updated.
    """

    stock_id: UUID
    product_id: UUID
    name: str
    total_stock: int
    reserved_stock: int
    available_stock: int
    created_at: datetime
    updated_at: datetime


class GetWarehouseStockResponseSchema(BaseModel):
    """Schema representing the response for get warehouse stock.

    Attributes:
        warehouse_stock (list[WarehouseStockItemSchema]): A list of warehouse stock items.
        page (int): The page number.
        page_size (int): The page size.
        elements (int): The number of elements.
    """

    warehouse_stock: list[WarehouseStockItemSchema]
    page: int
    page_size: int
    elements: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "warehouse_stock": [
                    {
                        "stock_id": "00000000-0000-0000-0000-000000000000",
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "name": "Product name",
                        "total_stock": 100,
                        "reserved_stock": 50,
                        "available_stock": 40,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    },
                    {
                        "stock_id": "00000000-0000-0000-0000-000000000000",
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "name": "Product name",
                        "total_stock": 100,
                        "reserved_stock": 50,
                        "available_stock": 40,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    },
                ],
                "page": 1,
                "page_size": 10,
                "elements": 2,
            }
        }
    }
