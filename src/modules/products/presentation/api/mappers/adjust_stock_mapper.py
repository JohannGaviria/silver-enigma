"""This module contains the adjust stock  api mapper."""

from uuid import UUID

from src.modules.products.application.dtos.adjust_stock_dto import (
    AdjustStockCommandDto,
    AdjustStockResponseDto,
)
from src.modules.products.presentation.api.schemas.adjust_stock_schema import (
    AdjustStockRequestSchema,
    AdjustStockResponseSchema,
)


class AdjustStockApiMapper:
    """Mapper for the adjust stock api."""

    @staticmethod
    def to_command(
        request: AdjustStockRequestSchema,
        product_id: UUID,
        warehouse_id: UUID,
    ) -> AdjustStockCommandDto:
        """Map an AdjustStockRequestSchema to an AdjustStockCommandDto.

        Args:
            request (AdjustStockRequestSchema): The AdjustStockRequestSchema to be mapped.
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.

        Returns:
            AdjustStockCommandDto: The mapped AdjustStockCommandDto.
        """
        return AdjustStockCommandDto(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=request.quantity,
        )

    @staticmethod
    def to_response(command: AdjustStockResponseDto) -> AdjustStockResponseSchema:
        """Map an AdjustStockResponseDto to an AdjustStockResponseSchema.

        Args:
            command (AdjustStockResponseDto): The AdjustStockResponseDto to be mapped.

        Returns:
            AdjustStockResponseSchema: The mapped AdjustStockResponseSchema.
        """
        return AdjustStockResponseSchema(
            id=command.id,
            product_id=command.product_id,
            warehouse_id=command.warehouse_id,
            total_stock=command.total_stock,
            reserved_stock=command.reserved_stock,
            available_stock=command.available_stock,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
