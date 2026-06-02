"""This module contains the ToggleProductStatusApiMapper class."""

from uuid import UUID

from src.modules.products.application.dtos.toggle_product_status_dto import (
    ToggleProductStatusCommandDto,
    ToggleProductStatusResponseDto,
)
from src.modules.products.presentation.api.schemas.toggle_product_status_schema import (
    ToggleProductStatusRequestSchema,
    ToggleProductStatusResponseSchema,
)


class ToggleProductStatusApiMapper:
    """Mapper for the toggle product status API."""

    @staticmethod
    def to_command(
        request: ToggleProductStatusRequestSchema, product_id: UUID
    ) -> ToggleProductStatusCommandDto:
        """Map a ToggleProductStatusRequestSchema to a ToggleProductStatusCommandDto.

        Args:
            request (ToggleProductStatusRequestSchema): The request schema to map.
            product_id (UUID): The ID of the product to update.

        Returns:
            ToggleProductStatusCommandDto: The mapped command.
        """
        return ToggleProductStatusCommandDto(
            product_id=product_id,
            is_active=request.is_active,
        )

    @staticmethod
    def to_response(
        command: ToggleProductStatusResponseDto,
    ) -> ToggleProductStatusResponseSchema:
        """Map a ToggleProductStatusResponseDto to a ToggleProductStatusResponseSchema.

        Args:
            command (ToggleProductStatusResponseDto): The response to map.

        Returns:
            ToggleProductStatusResponseSchema: The mapped response.
        """
        return ToggleProductStatusResponseSchema(
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
