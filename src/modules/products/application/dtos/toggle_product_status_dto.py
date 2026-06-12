"""This module contains the ToggleProductStatusUseeCase class."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum


@dataclass(frozen=True)
class ToggleProductStatusCommandDto:
    """DTO representing the command to toggle the status of a product.

    Attributes:
        product_id (UUID): The ID of the product to toggle the status of.
        is_active (bool): The new status of the product.
    """

    product_id: UUID
    is_active: bool


@dataclass(frozen=True)
class ToggleProductStatusResponseDto:
    """DTO representing the response from the ToggleProductStatusUseCase.

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
