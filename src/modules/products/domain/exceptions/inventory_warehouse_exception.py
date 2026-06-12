"""This module contains the inventory warehouse domain exceptions."""

from uuid import UUID

from src.shared.domain.exceptions.base_exception import BaseDomainException


class ReferencedWarehouseNotFoundException(BaseDomainException):
    """Exception raised when a referenced warehouse is not found."""

    def __init__(self) -> None:
        """Initializes the ReferencedWarehouseNotFoundException."""
        super().__init__("Referenced warehouse with ID not found.")


class ReferencedWarehouseNotActiveException(BaseDomainException):
    """Exception raised when a referenced warehouse is not active."""

    def __init__(self) -> None:
        """Initializes the ReferencedWarehouseNotActiveException."""
        super().__init__("Referenced warehouse is not active.")


class InvalidReferencedWarehouseException(BaseDomainException):
    """Exception raised when a referenced warehouse is invalid."""

    def __init__(self, errors: list[str], warehouse_id: UUID):
        """Initializes the InvalidReferencedWarehouseException.

        Args:
            errors (list[str]): A list of error messages.
            warehouse_id (UUID): The ID of the warehouse.
        """
        self.errors = errors
        self.warehouse_id = warehouse_id
        super().__init__("Referenced warehouse is invalid.")
