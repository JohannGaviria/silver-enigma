"""This module contains the UnitPriceVO class."""

from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class UnitPriceVO(BaseValueObject):
    """Value object representing a unit price.

    Attributes:
        price (Decimal): The unit price of the product.
    """

    price: Decimal

    def _validate(self) -> None:
        """Validates the UnitPriceVO.

        This method checks if the price is valid and raises an exception if it
        is not. It ensures that the price is not empty and is not negative.

        Raises:
            ValueError: If the price is invalid.
        """
        errors: list[str] = []

        if self.price is None:
            errors.append("Price cannot be empty.")
        if self.price < Decimal("0"):
            errors.append("Price cannot be negative.")

        if errors:
            raise ValueError(errors, self.price)
