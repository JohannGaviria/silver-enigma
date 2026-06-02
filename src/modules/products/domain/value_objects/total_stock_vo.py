"""This module contains the TotalStockVO class."""

from dataclasses import dataclass

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidTotalStockException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class TotalStockVO(BaseValueObject):
    """Value object representing the total number of stock items.

    Attributes:
        total_stock (int): The total number of stock items.
    """

    total_stock: int

    def _validate(self) -> None:
        """Validates the TotalStockVO.

        This method checks if the total stock is valid and raises an exception if it
        is not. It ensures that the total stock is not negative.

        Raises:
            InvalidTotalStockException: If the total stock is invalid.
        """
        errors: list[str] = []

        if self.total_stock is None:
            raise InvalidTotalStockException(
                "Total stock cannot be empty.", self.total_stock
            )
        if self.total_stock < 0:
            errors.append("Total stock cannot be negative.")

        if errors:
            raise InvalidTotalStockException(errors, self.total_stock)

    def value(self) -> int:
        """Returns the value of the TotalStockVO.

        Returns:
            int: The value of the TotalStockVO.
        """
        return self.total_stock
