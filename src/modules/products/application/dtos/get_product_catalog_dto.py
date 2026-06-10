"""This module contains the dto's for GetProductCatalogDto class."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_stock_item_vo import (
    ProductStockItemVO,
)
from src.modules.products.domain.value_objects.product_stock_vo import ProductStockVO


@dataclass(frozen=True)
class GetProductCatalogCommandDto:
    """DTO representing the command for get product catalog.

    Attributes:
        name (str | None): The name of the product to filter by.
        unit_of_measure (UnitOfMeasureEnum | None): The unit of measure of the product to filter by.
        page (int): The page number.
        page_size (int): The page size.
    """

    name: str | None
    unit_of_measure: UnitOfMeasureEnum | None
    page: int
    page_size: int


@dataclass(frozen=True)
class ProductStockItemDto:
    """DTO representing the product stock item.

    Attributes:
        product_id (UUID): Unique identifier of the product.
        name (str): Name of the product.
        description (str): Description of the product.
        unit_of_measure (UnitOfMeasureEnum): Unit of measure of the product.
        unit_price (Decimal): Unit price of the product.
        stock_disponible (int): Stock disponible of the product.
    """

    product_id: UUID
    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal
    stock_disponible: int

    @classmethod
    def from_vo(
        cls, product_stock_item_vo: ProductStockItemVO
    ) -> "ProductStockItemDto":
        """Creates a ProductStockItemDto from a ProductStockItemVO.

        Args:
            product_stock_item_vo (ProductStockItemVO): The product stock item VO.

        Returns:
            ProductStockItemDto: The product stock item DTO.
        """
        return cls(
            product_id=product_stock_item_vo.product_id,
            name=str(product_stock_item_vo.name),
            description=str(product_stock_item_vo.description),
            unit_of_measure=product_stock_item_vo.unit_of_measure,
            unit_price=product_stock_item_vo.unit_price,
            stock_disponible=product_stock_item_vo.total_stock.value()
            - product_stock_item_vo.available_stock.value(),
        )


@dataclass(frozen=True)
class GetProductCatalogResponseDto:
    """DTO representing the response for get product catalog.

    Attributes:
        products (list[ProductStockItemDto]): The list of product stock.
        page (int): The page number.
        page_size (int): The page size.
        elements (int): The number of elements.
    """

    products: list[ProductStockItemDto]
    page: int
    page_size: int
    elements: int

    @classmethod
    def from_stocks(
        cls, products_stock: ProductStockVO
    ) -> "GetProductCatalogResponseDto":
        """Creates a GetProductCatalogResponseDto from a ProductStockVO.

        Args:
            products_stock (ProductStockVO): The product stock VO.

        Returns:
            GetProductCatalogResponseDto: The GetProductCatalogResponseDto.
        """
        return cls(
            products=[
                ProductStockItemDto.from_vo(ps) for ps in products_stock.products_stock
            ],
            page=products_stock.page,
            page_size=products_stock.page_size,
            elements=products_stock.elements,
        )
