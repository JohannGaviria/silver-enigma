"""This module contains the ToggleWarehouseStatusApiMapper class."""

from uuid import UUID

from src.modules.warehouses.application.dtos.toggle_warehouse_status_dto import (
    ToggleWarehouseStatusCommandDto,
    ToggleWarehouseStatusResponseDto,
)
from src.modules.warehouses.presentation.api.schemas.toggle_warehouse_status_schema import (
    ToggleWarehouseStatusRequestSchema,
    ToggleWarehouseStatusResponseSchema,
)


class ToggleWarehouseStatusApiMapper:
    """Mapper for the toggle warehouse status API."""

    @staticmethod
    def to_command(
        request: ToggleWarehouseStatusRequestSchema, warehouse_id: UUID
    ) -> ToggleWarehouseStatusCommandDto:
        """Map a ToggleWarehouseStatusRequestSchema to a ToggleWarehouseStatusCommandDto.

        Args:
            request (ToggleWarehouseStatusRequestSchema): The request schema.
            warehouse_id (UUID): The ID of the warehouse to toggle.

        Returns:
            ToggleWarehouseStatusCommandDto: The command DTO.
        """
        return ToggleWarehouseStatusCommandDto(
            warehouse_id=warehouse_id,
            is_active=request.is_active,
        )

    @staticmethod
    def to_response(
        command: ToggleWarehouseStatusResponseDto,
    ) -> ToggleWarehouseStatusResponseSchema:
        """Map a ToggleWarehouseStatusResponseDto to a ToggleWarehouseStatusResponseSchema.

        Args:
            command (ToggleWarehouseStatusResponseDto): The response DTO.

        Returns:
            ToggleWarehouseStatusResponseSchema: The response schema.
        """
        return ToggleWarehouseStatusResponseSchema(
            id=command.id,
            supplier_id=command.supplier_id,
            name=command.name,
            address=command.address,
            is_active=command.is_active,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
