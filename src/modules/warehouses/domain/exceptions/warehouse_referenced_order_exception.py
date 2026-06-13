"""This module contains the exceptions for warehouse referenced order."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidWarehouseReferencedOrderException(BaseDomainException):
    """Exception raised when a warehouse referenced order is invalid."""

    def __init__(self, error: str):
        """Initialize the InvalidWarehouseReferencedOrderException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid warehouse referenced order.")
