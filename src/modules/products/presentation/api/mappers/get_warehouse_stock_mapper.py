"""This module contains the GetWarehouseStockApiMapper class."""

from uuid import UUID

from src.modules.products.application.dtos.get_warehouse_stock_dto import (
    GetWarehouseStockCommandDto,
    GetWarehouseStockResponseDto,
    WarehouseStockItemDto,
)
from src.modules.products.presentation.api.schemas.get_warehouse_stock_schema import (
    GetWarehouseStockResponseSchema,
    WarehouseStockItemSchema,
)


class GetWarehouseStockApiMapper:
    """Mapper for the GetWarehouseStockUseCase."""

    @staticmethod
    def to_command(
        warehouse_id: UUID, page: int, page_size: int
    ) -> GetWarehouseStockCommandDto:
        """Convert a GetWarehouseStockResponseDto to a GetWarehouseStockCommandDto.

        Args:
            warehouse_id (UUID): The ID of the warehouse.
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            GetWarehouseStockCommandDto: The GetWarehouseStockCommandDto instance.
        """
        return GetWarehouseStockCommandDto(
            warehouse_id=warehouse_id,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def to_item(
        warehouse_stock_item: WarehouseStockItemDto,
    ) -> WarehouseStockItemSchema:
        """Convert a WarehouseStockItemVO to a WarehouseStockItemSchema.

        Args:
            warehouse_stock_item (WarehouseStockItemVO): The warehouse stock item VO.

        Returns:
            WarehouseStockItemSchema: The WarehouseStockItemSchema instance.
        """
        return WarehouseStockItemSchema(
            stock_id=warehouse_stock_item.stock_id,
            product_id=warehouse_stock_item.product_id,
            name=warehouse_stock_item.name,
            total_stock=warehouse_stock_item.total_stock,
            available_stock=warehouse_stock_item.available_stock,
            stock_disponible=warehouse_stock_item.stock_disponible,
            created_at=warehouse_stock_item.created_at,
            updated_at=warehouse_stock_item.updated_at,
        )

    @classmethod
    def to_response(
        cls, response: GetWarehouseStockResponseDto
    ) -> GetWarehouseStockResponseSchema:
        """Convert a GetWarehouseStockResponseDto to a GetWarehouseStockResponseSchema.

        Args:
            response (GetWarehouseStockResponseDto): The GetWarehouseStockResponseDto instance.

        Returns:
            GetWarehouseStockResponseSchema: The GetWarehouseStockResponseSchema instance.
        """
        return GetWarehouseStockResponseSchema(
            warehouse_stock=[cls.to_item(ws) for ws in response.warehouse_stock],
            page=response.page,
            page_size=response.page_size,
            elements=response.elements,
        )
