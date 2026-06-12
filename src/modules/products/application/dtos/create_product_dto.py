"""This module contains the dto's for CreateProductUseCase."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


@dataclass(frozen=True)
class BaseCreateProductDto:
    """Base DTO representing the command for create product.

    Attributes:
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to
            measure the product.
        unit_price (Decimal): The unit price of the product.
    """

    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal


@dataclass(frozen=True)
class CreateProductCommandDto(BaseCreateProductDto):
    """DTO representing the command for create product.

    Attributes:
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to
            measure the product.
        unit_price (Decimal): The unit price of the product.
    """

    ...


@dataclass(frozen=True)
class CreateProductResponseDto(BaseCreateProductDto):
    """DTO Representing the response for create product.

    Attributes:
        id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier that owns the product.
        name (str): The name of the product.
        description (str): A description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure used to
            measure the product.
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
