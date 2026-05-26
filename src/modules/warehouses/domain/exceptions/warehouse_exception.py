"""This module contains the exceptions for the warehouse."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidWarehouseNameException(BaseDomainException):
    """Exception raised when a warehouse name is invalid."""

    def __init__(self, name: str, errors: list[str]):
        """Initialize the InvalidWarehouseNameException.

        Args:
            name (str): The invalid name.
            errors (list[str]): A list of errors associated with the name.
        """
        self.name = name
        self.errors = errors
        super().__init__("Invalid warehouse name.")


class InvalidWarehouseAddressException(BaseDomainException):
    """Exception raised when a warehouse address is invalid."""

    def __init__(self, address: str, errors: list[str]):
        """Initialize the InvalidWarehouseAddressException.

        Args:
            address (str): The invalid address.
            errors (list[str]): A list of errors associated with the address.
        """
        self.address = address
        self.errors = errors
        super().__init__("Invalid warehouse address.")
