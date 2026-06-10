"""This module contains the ProductStockItemVO class."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO


@dataclass(frozen=True)
class ProductStockItemVO:
    """Value Object representing the product stock item.

    Attributes:
        product_id (UUID): Unique identifier of the product.
        name (str): Name of the product.
        description (str): Description of the product.
        unit_of_measure (UnitOfMeasureEnum): Unit of measure of the product.
        unit_price (Decimal): Unit price of the product.
        total_stock (TotalStockVO): Total stock of the product.
        available_stock (AvailableStockVO): Available stock of the product.
    """

    product_id: UUID
    name: str
    description: str
    unit_of_measure: UnitOfMeasureEnum
    unit_price: Decimal
    total_stock: TotalStockVO
    available_stock: AvailableStockVO
