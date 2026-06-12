"""This module contains the ReservedStockVO class."""

from dataclasses import dataclass

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidReservedStockException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ReservedStockVO(BaseValueObject):
    """Value object representing the number of reserved stock items.

    Attributes:
        reserved_stock (int): The number of reserved stock items.
    """

    reserved_stock: int

    def _validate(self) -> None:
        """Validates the ReservedStockVO.

        This method checks if the reserved stock is valid and raises an exception if it
        is not. It ensures that the reserved stock is not negative.

        Raises:
            InvalidReservedStockException: If the reserved stock is invalid.
        """
        errors: list[str] = []

        if self.reserved_stock is None:
            raise InvalidReservedStockException(
                "Reserved stock cannot be empty.", self.reserved_stock
            )
        if self.reserved_stock < 0:
            errors.append("Reserved stock cannot be negative.")

        if errors:
            raise InvalidReservedStockException(errors, self.reserved_stock)

    def value(self) -> int:
        """Returns the value of the ReservedStockVO.

        Returns:
            int: The value of the ReservedStockVO.
        """
        return self.reserved_stock
