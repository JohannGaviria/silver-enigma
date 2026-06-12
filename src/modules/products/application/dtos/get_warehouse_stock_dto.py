"""This module contains the DTO's for GetWarehouseStockUseCase class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.products.domain.value_objects.warehouse_stock_item_vo import (
    WarehouseStockItemVO,
)
from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)


@dataclass(frozen=True)
class GetWarehouseStockCommandDto:
    """DTO representing the command for get warehouse stock.

    Attributes:
        warehouse_id (UUID): The ID of the warehouse to get the stock for.
        page (int): The page number.
        page_size (int): The page size.
    """

    warehouse_id: UUID
    page: int
    page_size: int


@dataclass(frozen=True)
class WarehouseStockItemDto:
    """DTO representing a warehouse stock item.

    Attributes:
        stock_id (UUID): The ID of the warehouse stock item.
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

    @classmethod
    def from_vo(
        cls, warehouse_stock_item_vo: WarehouseStockItemVO
    ) -> "WarehouseStockItemDto":
        """Creates a WarehouseStockItemDto from a WarehouseStockItemVO.

        Args:
            warehouse_stock_item_vo (WarehouseStockItemVO): The warehouse stock item VO.

        Returns:
            WarehouseStockItemDto: The warehouse stock item DTO.
        """
        return cls(
            stock_id=warehouse_stock_item_vo.stock_id,
            product_id=warehouse_stock_item_vo.product_id,
            name=str(warehouse_stock_item_vo.name),
            total_stock=warehouse_stock_item_vo.total_stock.value(),
            reserved_stock=warehouse_stock_item_vo.reserved_stock.value(),
            available_stock=warehouse_stock_item_vo.available_stock,
            created_at=warehouse_stock_item_vo.created_at,
            updated_at=warehouse_stock_item_vo.updated_at,
        )


@dataclass(frozen=True)
class GetWarehouseStockResponseDto:
    """DTO representing the response for get warehouse stock.

    Attributes:
        warehouse_stock (list[WarehouseStockItemDto]): A list of warehouse stock items.
        page (int): The page number.
        page_size (int): The page size.
        elements (int): The number of elements.
    """

    warehouse_stock: list[WarehouseStockItemDto]
    page: int
    page_size: int
    elements: int

    @classmethod
    def from_stocks(
        cls, warehouse_stock: WarehouseStockVO
    ) -> "GetWarehouseStockResponseDto":
        """Creates a GetWarehouseStockResponseDto from a list of WarehouseStockItemVO.

        Args:
            warehouse_stock (list[WarehouseStockItemVO]): The list of warehouse stock items.

        Returns:
            GetWarehouseStockResponseDto: The GetWarehouseStockResponseDto.
        """
        return cls(
            warehouse_stock=[
                WarehouseStockItemDto.from_vo(ws)
                for ws in warehouse_stock.warehouse_stock
            ],
            page=warehouse_stock.page,
            page_size=warehouse_stock.page_size,
            elements=warehouse_stock.elements,
        )
