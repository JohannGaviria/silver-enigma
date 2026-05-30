"""This module contains the UpdateWarehouseApiMapper class."""

from uuid import UUID

from src.modules.warehouses.application.dtos.update_warehouse_dto import (
    UpdateWarehouseCommandDto,
    UpdateWarehouseResponseDto,
)
from src.modules.warehouses.presentation.api.schemas.update_warehouse_schema import (
    UpdateWarehouseRequestSchema,
    UpdateWarehouseResponseSchema,
)


class UpdateWarehouseApiMapper:
    """Mapper for the update warehouse API."""

    @staticmethod
    def to_command(
        request: UpdateWarehouseRequestSchema, warehouse_id: UUID
    ) -> UpdateWarehouseCommandDto:
        """Map a UpdateWarehouseRequestSchema to a UpdateWarehouseCommandDto.

        Args:
            request (UpdateWarehouseRequestSchema): The request schema.
            warehouse_id (UUID): The ID of the warehouse to update.

        Returns:
            UpdateWarehouseCommandDto: The command DTO.
        """
        return UpdateWarehouseCommandDto(
            warehouse_id=warehouse_id,
            name=request.name,
            address=request.address,
        )

    @staticmethod
    def to_response(
        command: UpdateWarehouseResponseDto,
    ) -> UpdateWarehouseResponseSchema:
        """Map a UpdateWarehouseResponseDto to a UpdateWarehouseResponseSchema.

        Args:
            command (UpdateWarehouseResponseDto): The response DTO.

        Returns:
            UpdateWarehouseResponseSchema: The response schema.
        """
        return UpdateWarehouseResponseSchema(
            id=command.id,
            supplier_id=command.supplier_id,
            name=command.name,
            address=command.address,
            is_active=command.is_active,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
