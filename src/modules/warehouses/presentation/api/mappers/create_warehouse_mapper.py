"""This module contains the CreateWarehouseApiMapper class."""

from uuid import UUID

from src.modules.warehouses.application.dtos.create_warehouse_dto import (
    CreateWarehouseCommandDto,
    CreateWarehouseResponseDto,
)
from src.modules.warehouses.presentation.api.schemas.create_warehouse_schema import (
    CreateWarehouseRequestSchema,
    CreateWarehouseResponseSchema,
)


class CreateWarehouseApiMapper:
    """This class contains methods for mapping between the API and the application layer."""

    @staticmethod
    def to_command(
        request: CreateWarehouseRequestSchema, supplier_id: UUID
    ) -> CreateWarehouseCommandDto:
        """Map a request schema to a command DTO.

        Args:
            request (CreateWarehouseRequestSchema): The request schema to map.
            supplier_id (UUID): The supplier ID associated with the warehouse.

        Returns:
            CreateWarehouseCommandDto: The command DTO.
        """
        return CreateWarehouseCommandDto(
            supplier_id=supplier_id, name=request.name, address=request.address
        )

    @staticmethod
    def to_response(
        command: CreateWarehouseResponseDto,
    ) -> CreateWarehouseResponseSchema:
        """Map a command DTO to a response schema.

        Args:
            command (CreateWarehouseResponseDto): The command DTO to map.

        Returns:
            CreateWarehouseResponseSchema: The response schema.
        """
        return CreateWarehouseResponseSchema(
            id=command.id,
            supplier_id=command.supplier_id,
            name=command.name,
            address=command.address,
            is_active=command.is_active,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
