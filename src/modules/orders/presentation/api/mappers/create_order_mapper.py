"""This module contains the CreateOrderApiMapper class."""

from src.modules.orders.application.dtos.create_order_dto import (
    CreateOrderCommandDto,
    CreateOrderResponseDto,
    ProductDetailsDto,
    ProductItemsDto,
)
from src.modules.orders.presentation.api.schemas.create_order_schema import (
    CreateOrderRequestSchema,
    CreateOrderResponseSchema,
    ProductDetailsSchema,
    ProductItemSchema,
)


class CreateOrderApiMapper:
    """Class responsible for mapping CreateOrderDto to CreateOrderApiSchema."""

    @staticmethod
    def to_item(item: ProductItemSchema) -> ProductItemsDto:
        """Map a ProductItemSchema to a ProductItemsDto.

        Args:
            item (ProductItemSchema): The ProductItemSchema to map.

        Returns:
            ProductItemsDto: The mapped ProductItemsDto.
        """
        return ProductItemsDto(
            product_id=item.product_id,
            quantity=item.quantity,
        )

    @staticmethod
    def to_command(request: CreateOrderRequestSchema) -> CreateOrderCommandDto:
        """Map a CreateOrderRequestSchema to a CreateOrderCommandDto.

        Args:
            request (CreateOrderRequestSchema): The CreateOrderRequestSchema to map.

        Returns:
            CreateOrderCommandDto: The mapped CreateOrderCommandDto.
        """
        return CreateOrderCommandDto(
            items=[CreateOrderApiMapper.to_item(item) for item in request.items]
        )

    @staticmethod
    def to_details(details: ProductDetailsDto) -> ProductDetailsSchema:
        """Map a ProductDetailsDto to a ProductDetailsSchema.

        Args:
            details (ProductDetailsDto): The ProductDetailsDto to map.

        Returns:
            ProductDetailsSchema: The mapped ProductDetailsSchema.
        """
        return ProductDetailsSchema(
            product_id=details.product_id,
            quantity=details.quantity,
            name=details.name,
            unit_price=details.unit_price,
        )

    @staticmethod
    def to_response(command: CreateOrderResponseDto) -> CreateOrderResponseSchema:
        """Map a CreateOrderResponseDto to a CreateOrderResponseSchema.

        Args:
            command (CreateOrderResponseDto): The CreateOrderResponseDto to map.

        Returns:
            CreateOrderResponseSchema: The mapped CreateOrderResponseSchema.
        """
        return CreateOrderResponseSchema(
            id=command.id,
            buyer_id=command.buyer_id,
            items=[CreateOrderApiMapper.to_details(item) for item in command.items],
            status=command.status.value,
            created_at=command.created_at,
            updated_at=command.updated_at,
        )
