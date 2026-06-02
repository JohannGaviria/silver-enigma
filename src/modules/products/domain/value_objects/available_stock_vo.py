"""This module contains the AvailableStockVO class."""

from dataclasses import dataclass

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidAvailableStockException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class AvailableStockVO(BaseValueObject):
    """Value object representing the number of available stock items.

    Attributes:
        available_stock (int): The number of available stock items.
    """

    available_stock: int

    def _validate(self) -> None:
        """Validates the AvailableStockVO.

        This method checks if the available stock is valid and raises an exception if it
        is not. It ensures that the available stock is not negative.

        Raises:
            InvalidAvailableStockException: If the available stock is invalid.
        """
        errors: list[str] = []

        if self.available_stock is None:
            raise InvalidAvailableStockException(
                "Available stock cannot be empty.", self.available_stock
            )
        if self.available_stock < 0:
            errors.append("Available stock cannot be negative.")

        if errors:
            raise InvalidAvailableStockException(errors, self.available_stock)

    def value(self) -> int:
        """Returns the value of the AvailableStockVO.

        Returns:
            int: The value of the AvailableStockVO.
        """
        return self.available_stock
