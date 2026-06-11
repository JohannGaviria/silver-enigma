"""This module contains the dto's for AdjustStockUseCase class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BaseAdjustStockDto:
    """Base DTO for adjusting stock.

    Attributes:
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
    """

    product_id: UUID
    warehouse_id: UUID


@dataclass(frozen=True)
class AdjustStockCommandDto(BaseAdjustStockDto):
    """Command DTO for adjusting stock.

    Attributes:
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        quantity (int): The quantity to adjust stock by.
    """

    quantity: int


@dataclass(frozen=True)
class AdjustStockResponseDto(BaseAdjustStockDto):
    """Response DTO for adjusting stock.

    Attributes:
        id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        total_stock (int): The total stock after adjusting.
        reserved_stock (int): The reserved stock after adjusting.
        stock_disponible (int): The stock that can be dispensed.
        created_at (datetime): The date and time the command was created.
        updated_at (datetime): The date and time the command was updated.
    """

    id: UUID
    total_stock: int
    reserved_stock: int
    stock_disponible: int
    created_at: datetime
    updated_at: datetime
