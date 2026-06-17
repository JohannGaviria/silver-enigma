"""This module contains the ReferencedProductVO class."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.modules.orders.domain.exceptions.order_exception import (
    InvalidReferencedProductException,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ReferencedProductVO(BaseValueObject):
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

    def _validate(self) -> None:
        """Validate the referenced product.

        This method checks if the product ID, supplier ID, name, quantity, unit price, and is active are valid.

        Raises:
            InvalidReferencedProductException: If any of the values are invalid.
        """
        errors: list[str] = []

        if self.product_id is None:
            errors.append("Product ID cannot be None.")
        if self.supplier_id is None:
            errors.append("Supplier ID cannot be None.")
        if self.name is None:
            errors.append("Name cannot be None.")
        if self.quantity is None:
            errors.append("Quantity cannot be None.")
        if self.unit_price is None:
            errors.append("Unit price cannot be None.")
        if self.is_active is None:
            errors.append("Is active cannot be None.")

        if errors:
            raise InvalidReferencedProductException(errors)
