"""This module contains the adjust stock schema."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdjustStockRequestSchema(BaseModel):
    """Request schema for the adjust stock.

    Attributes:
        quantity (int): The quantity to adjust the stock for.
    """

    quantity: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "quantity": 10,
            }
        }
    }


class AdjustStockResponseSchema(BaseModel):
    """Response schema for the adjust stock.

    Attributes:
        id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        total_stock (int): The total number of items in stock.
        available_stock (int): The number of items available for purchase.
        stock_disponible (int): The number of items available for purchase.
        created_at (datetime): The date and time the stock was created.
        updated_at (datetime): The date and time the stock was updated.
    """

    id: UUID
    product_id: UUID
    warehouse_id: UUID
    total_stock: int
    available_stock: int
    stock_disponible: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "product_id": "00000000-0000-0000-0000-000000000000",
                "warehouse_id": "00000000-0000-0000-0000-000000000000",
                "total_stock": 100,
                "available_stock": 50,
                "stock_disponible": 50,
                "created_at": "2026-06-08 18:28:46.815704+00:00",
                "updated_at": "2026-06-08 18:28:46.815704+00:00",
            }
        }
    }
