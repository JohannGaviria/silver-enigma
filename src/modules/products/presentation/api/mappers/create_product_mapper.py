"""This module contains the CreateProductApiMapper class."""

from src.modules.products.application.dtos.create_product_dto import (
    CreateProductCommandDto,
    CreateProductResponseDto,
)
from src.modules.products.presentation.api.schemas.create_product_schema import (
    CreateProductRequestSchema,
    CreateProductResponseSchema,
)


class CreateProductApiMapper:
    """Class responsible for mapping CreateProductSchema to CreateProductDto."""

    @staticmethod
    def to_command(request: CreateProductRequestSchema) -> CreateProductCommandDto:
        """Map a CreateProductRequestSchema to a CreateProductDto.

        Args:
            request (CreateProductRequestSchema): The CreateProductRequestSchema to map.

        Returns:
            CreateProductDto: The mapped CreateProductDto.
        """
        return CreateProductCommandDto(
            name=request.name,
            description=request.description,
            unit_of_measure=request.unit_of_measure,
            unit_price=request.unit_price,
        )

    @staticmethod
    def to_response(command: CreateProductResponseDto) -> CreateProductResponseSchema:
        """Map a CreateProductDto to a CreateProductResponseSchema.

        Args:
            command (CreateProductDto): The CreateProductDto to map.

        Returns:
            CreateProductResponseSchema: The mapped CreateProductResponseSchema.
        """
        return CreateProductResponseSchema(
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
