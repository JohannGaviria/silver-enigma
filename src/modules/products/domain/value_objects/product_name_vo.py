"""This module contains the ProductNameVO class."""

from dataclasses import dataclass

from src.modules.products.domain.exceptions.product_exception import (
    InvalidProductNameException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ProductNameVO(BaseValueObject):
    """Value object representing a product name.

    Attributes:
        name (str): The name of the product.
    """

    name: str

    def _validate(self) -> None:
        """Validates the ProductNameVO.

        This method checks if the name is valid and raises an exception if it
        is not. It ensures that the name is not empty, has at least 3 characters,
        and is not longer than 150 characters.

        Raises:
            InvalidProductNameException: If the name is invalid.
        """
        errors: list[str] = []

        if self.name is None or not self.name.strip():
            errors.append("Name cannot be empty.")
        if len(self.name) < 3:
            errors.append("Name must be at least 3 characters long.")
        if len(self.name) >= 150:
            errors.append("Name cannot be longer than 150 characters.")

        if errors:
            raise InvalidProductNameException(errors, self.name)

    def __str__(self) -> str:
        """Returns the string representation of the ProductNameVO.

        Returns:
            str: The string representation of the ProductNameVO.
        """
        return self.name
