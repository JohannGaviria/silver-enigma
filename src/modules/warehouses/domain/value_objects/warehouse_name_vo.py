"""This module contains the WarehouseNameVO class."""

from dataclasses import dataclass

from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseNameException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class WarehouseNameVO(BaseValueObject):
    """Value Object for a Warehouse Name.

    This value object represents a warehouse name and provides validation
    methods to ensure that the name is valid.

    Attributes:
        name (str): The name of the warehouse.
    """

    name: str

    def _validate(self) -> None:
        """Validate the WarehouseNameVO.

        The validation checks include:
        - Check if the name is not empty.
        - Check if the name is at least 3 characters long.
        - Check if the name is not longer than 100 characters.

        Raises:
            InvalidWarehouseNameException: If the name is invalid.
        """
        errors: list[str] = []

        if self.name is None or not self.name.strip():
            errors.append("Name cannot be empty.")
        if len(self.name) < 3:
            errors.append("Name must be at least 3 characters.")
        if len(self.name) >= 100:
            errors.append("Name cannot be longer than 100 characters.")

        if errors:
            raise InvalidWarehouseNameException(self.name, errors)

    def __str__(self) -> str:
        """Return the string representation of the WarehouseNameVO.

        Returns:
            str: The string representation of the WarehouseNameVO.
        """
        return self.name
