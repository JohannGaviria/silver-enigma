"""This module contains the WarehouseAddressVO class."""

from dataclasses import dataclass

from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseAddressException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class WarehouseAddressVO(BaseValueObject):
    """Value Object for a Warehouse Address.

    This value object represents a warehouse address and provides validation
    methods to ensure that the address is valid.

    Attributes:
        address (str): The address of the warehouse.
    """

    address: str

    def _validate(self) -> None:
        """Validate the WarehouseAddressVO.

        The validation checks include:
        - Check if the address is not empty.
        - Check if the address is at least 3 characters long.
        - Check if the address is not longer than 255 characters.

        Raises:
            InvalidWarehouseAddressException: If the address is invalid.
        """
        errors: list[str] = []

        if self.address is None or not self.address.strip():
            errors.append("Address cannot be empty.")
        if len(self.address) < 3:
            errors.append("Address must be at least 3 characters.")
        if len(self.address) >= 255:
            errors.append("Address cannot be longer than 255 characters.")

        if errors:
            raise InvalidWarehouseAddressException(self.address, errors)

    def __str__(self) -> str:
        """Return the string representation of the WarehouseAddressVO.

        Returns:
            str: The string representation of the WarehouseAddressVO.
        """
        return self.address
