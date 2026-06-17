"""This module contains the ReferencedProductVO class."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.modules.orders.domain.value_object.quantity_vo import QuantityVO


@dataclass(frozen=True)
class ReferencedProductVO:
    """Value object for a referenced product.

    Attributes:
        product_id (UUID): The ID of the product.
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the product.
        quantity (QuantityVO): The quantity of the product.
        unit_price (Decimal): The unit price of the product.
        is_active (bool): Whether the product is active.
    """

    product_id: UUID
    supplier_id: UUID
    name: str
    quantity: QuantityVO
    unit_price: Decimal
    is_active: bool
