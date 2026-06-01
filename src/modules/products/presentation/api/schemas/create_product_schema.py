"""This module contains the schema for the create product endpoint."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


class BaseCreateProductSchema(BaseModel):
    """Base schema for the create product endpoint.

    Attributes:
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to measure the product.
        unit_price (Decimal): The unit price of the product.
    """

    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal


class CreateProductRequestSchema(BaseCreateProductSchema):
    """Request schema for the create product endpoint.

    Attributes:
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to measure the product.
        unit_price (Decimal): The unit price of the product.
    """

    ...

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Product Name",
                "description": "Product Description",
                "unit_of_measure": "Unit of Measure",
                "unit_price": 10.00,
            }
        }
    }


class CreateProductResponseSchema(BaseCreateProductSchema):
    """Response schema for the create product endpoint.

    Attributes:
        id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier that owns the product.
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to measure the product.
        unit_price (Decimal): The unit price of the product.
        is_active (bool): A flag indicating whether the product is active.
        created_at (datetime): The datetime when the product was created.
        updated_at (datetime): The datetime when the product was last updated.
    """

    id: UUID
    supplier_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "c7444eff-7f23-482d-b415-e72dc51e6e4f",
                "supplier_id": "d97e303b-dcb3-4d1e-b25e-071e365affb3",
                "name": "Product Name",
                "description": "Product Description",
                "unit_of_measure": "Unit of Measure",
                "unit_price": 10.00,
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
            }
        }
    }
