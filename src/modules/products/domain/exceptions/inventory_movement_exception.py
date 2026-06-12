"""This module contains the inventory movement domain exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InventoryMovementRepositoryException(BaseDomainException):
    """Exception raised when an inventory movement repository operation fails."""

    def __init__(self, error: str):
        """Initializes the InventoryMovementRepositoryException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Inventory movement repository error.")
