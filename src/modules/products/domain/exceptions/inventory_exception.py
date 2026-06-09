"""This module contains the inventory exception classes."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InventoryRepositoryException(BaseDomainException):
    """Exception raised when an inventory repository operation fails."""

    def __init__(self, error: str) -> None:
        """Initializes the InventoryRepositoryException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Inventory repository error.")
