"""This module contains the QuantityVO class."""

from dataclasses import dataclass

from src.modules.orders.domain.exceptions.order_exception import (
    InvalidQuantityException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class QuantityVO(BaseValueObject):
    """Value object for quantity of an order.

    Attributes:
        quantity (int): Quantity of an order.
    """

    quantity: int

    def _validate(self) -> None:
        """Validate the quantity of the order.

        This method checks if the quantity is greater than 0.

        Raises:
            InvalidQuantityException: If the quantity is invalid.
        """
        errors: list[str] = []

        if self.quantity <= 0:
            errors.append("Quantity must be greater than 0.")

        if errors:
            raise InvalidQuantityException(errors, self.quantity)

    def value(self) -> int:
        """Return the quantity of the order.

        Returns:
            int: The quantity of the order.
        """
        return self.quantity
