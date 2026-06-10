"""This module contains the get product catalog schema."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


class ProductStockItemSchema(BaseModel):
    """Product stock item schema.

    Attributes:
        product_id (UUID): The ID of the product.
        name (str): The name of the product.
        description (str): The description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure of the product.
        unit_price (Decimal): The unit price of the product.
        stock_disponible (int): The stock disponible of the product.
    """

    product_id: UUID
    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal
    stock_disponible: int


class GetProductCatalogResponseSchema(BaseModel):
    """Get product catalog response schema.

    Attributes:
        products (list[ProductStockItemSchema]): The list of product stock items.
        page (int): The page number.
        page_size (int): The page size.
        elements (int): The number of elements.
    """

    products: list[ProductStockItemSchema]
    page: int
    page_size: int
    elements: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "products": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000000",
                        "name": "Premium Rice",
                        "description": "High quality rice",
                        "unit_of_measure": "KG",
                        "unit_price": 15.50,
                        "stock_disponible": 100,
                    }
                ],
                "page": 1,
                "page_size": 10,
                "elements": 1,
            }
        }
    }
