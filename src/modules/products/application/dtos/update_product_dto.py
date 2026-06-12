"""This module contains the UpdateProductUseCase class."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


@dataclass(frozen=True)
class UpdateProductCommandDto:
    """DTO representing the command to update a product.

    Attributes:
        product_id (UUID): The ID of the product to update.
        name (str | None): The name of the product.
        description (str | None): The description of the product.
        unit_of_measure (UnitOfMeasureEnum | None): The unit of measure of the product.
        unit_price (Decimal | None): The unit price of the product.
    """

    product_id: UUID
    name: str | None = None
    description: str | None = None
    unit_of_measure: UnitOfMeasureEnum | None = None
    unit_price: Decimal | None = None


@dataclass(frozen=True)
class UpdatedProductResponseDto:
    """DTO representing the response from the UpdateProductUseCase.

    Attributes:
        id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the product.
        description (str): The description of the product.
        unit_of_measure (UnitOfMeasureEnum): The unit of measure of the product.
        unit_price (Decimal): The unit price of the product.
        is_active (bool): Whether the product is active or not.
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
