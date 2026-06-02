"""This module contains the UpdateProductMapper class."""

from uuid import UUID

from src.modules.products.application.dtos.update_product_dto import (
    UpdateProductCommandDto,
    UpdatedProductResponseDto,
)
from src.modules.products.presentation.api.schemas.update_product_schema import (
    UpdateProductRequestSchema,
    UpdateProductResponseSchema,
)


class UpdateProductApiMapper:
    """Mapper for the update product API."""

    @staticmethod
    def to_command(
        request: UpdateProductRequestSchema, product_id: UUID
    ) -> UpdateProductCommandDto:
        """Map an UpdateProductRequestSchema to a UpdateProductCommandDto.

        Args:
            request (UpdateProductRequestSchema): The request schema to map.
            product_id (UUID): The ID of the product to update.

        Returns:
            UpdateProductCommandDto: The mapped command.
        """
        return UpdateProductCommandDto(
            product_id=product_id,
            name=request.name,
            description=request.description,
            unit_of_measure=request.unit_of_measure,
            unit_price=request.unit_price,
        )

    @staticmethod
    def to_response(command: UpdatedProductResponseDto) -> UpdateProductResponseSchema:
        """Map an UpdatedProductResponseDto to an UpdateProductResponseSchema.

        Args:
            command (UpdatedProductResponseDto): The response to map.

        Returns:
            UpdateProductResponseSchema: The mapped response.
        """
        return UpdateProductResponseSchema(
            id=command.id,
            supplier_id=command.supplier_id,
            name=command.name,
            description=command.description,
            unit_of_measure=command.unit_of_measure,
            unit_price=command.unit_price,
            is_active=command.is_active,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
