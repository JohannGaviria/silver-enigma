"""This module contains the get ProductCatalogApiMapper."""

from src.modules.products.application.dtos.get_product_catalog_dto import (
    GetProductCatalogCommandDto,
    GetProductCatalogResponseDto,
    ProductStockItemDto,
)
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.presentation.api.schemas.get_product_catalog_schema import (
    GetProductCatalogResponseSchema,
    ProductStockItemSchema,
)


class GetProductCatalogApiMapper:
    """Mapper for the GetProductCatalogUseCase."""

    @staticmethod
    def to_command(
        name: str | None,
        unit_of_measure: UnitOfMeasureEnum | None,
        page: int,
        page_size: int,
    ) -> GetProductCatalogCommandDto:
        """Convert the request schema to a command.

        Args:
            name (str | None): The name of the product to filter by.
            unit_of_measure (UnitOfMeasureEnum | None): The unit of measure of the product to filter by.
            page (int): The page number.
            page_size (int): The page size.

        Returns:
            GetProductCatalogCommandDto: The command.
        """
        return GetProductCatalogCommandDto(
            name=name,
            unit_of_measure=unit_of_measure,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def to_item(item: ProductStockItemDto) -> ProductStockItemSchema:
        """Convert the item to a item schema.

        Args:
            item (ProductStockItemDto): The item.

        Returns:
            ProductStockItemSchema: The item schema.
        """
        return ProductStockItemSchema(
            product_id=item.product_id,
            name=item.name,
            description=item.description,
            unit_of_measure=item.unit_of_measure,
            unit_price=item.unit_price,
            available_stock=item.available_stock,
        )

    @staticmethod
    def to_response(
        command: GetProductCatalogResponseDto,
    ) -> GetProductCatalogResponseSchema:
        """Convert the response to a response schema.

        Args:
            command (GetProductCatalogResponseDto): The response.

        Returns:
            GetProductCatalogResponseSchema: The response schema.
        """
        return GetProductCatalogResponseSchema(
            products=[
                GetProductCatalogApiMapper.to_item(item) for item in command.products
            ],
            page=command.page,
            page_size=command.page_size,
            elements=command.elements,
        )
