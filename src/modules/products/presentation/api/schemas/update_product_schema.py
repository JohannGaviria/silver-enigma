"""This module contains the UpdateProductSchema class."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


class UpdateProductRequestSchema(BaseModel):
    """Schema for the request to update a product.

    Attributes:
        name (str | None): The name of the product.
        description (str | None): The description of the product.
        unit_of_measure (UnitOfMeasureEnum | None): The unit of measure of the product.
        unit_price (Decimal | None): The unit price of the product.
    """

    name: str | None = None
    description: str | None = None
    unit_of_measure: UnitOfMeasureEnum | None = None
    unit_price: Decimal | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "New Product Name",
                "description": "New Product Description",
                "unit_of_measure": "UNIT",
                "unit_price": 100.50,
            }
        }
    }


class UpdateProductResponseSchema(BaseModel):
    """Schema for the response from the UpdateProductUseCase.

    Attributes:
        id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the product.
        description (str): The description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure of the product.
        unit_price (Decimal): The unit price of the product.
        is_active (bool): Whether the product is active.
        created_at (datetime): The date and time when the product was created.
        updated_at (datetime): The date and time when the product was last updated.
    """

    id: UUID
    supplier_id: UUID
    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "96ec96b5-cd06-432d-943b-127ec17b00f2",
                "supplier_id": "4e69ceba-46f8-4491-8b47-ed1714cbce96",
                "name": "New Product Name",
                "description": "New Product Description",
                "unit_of_measure": "UNIT",
                "unit_price": 100.50,
                "is_active": True,
                "created_at": "2026-06-02 18:28:46.815704+00:00",
                "updated_at": "2026-06-02 18:29:03.138247+00:00",
            }
        }
    }
