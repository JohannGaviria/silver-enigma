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


class WarehouseRepositoryException(BaseDomainException):
    """Exception raised for errors that occur within the WarehouseRepository."""

    def __init__(self, error: str) -> None:
        """Initialize the WarehouseRepositoryException.

        Args:
            error (str): A message describing the error that occurred within the WarehouseRepository.
        """
        self.error = error
        super().__init__("An error occurred in the WarehouseRepository.")
