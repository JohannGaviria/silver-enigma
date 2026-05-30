"""This module contains the session exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InsufficientPermissionsException(BaseDomainException):
    """Exception raised when user authentication fails due to insufficient permissions."""

    def __init__(self, error: str) -> None:
        """Initializes the InsufficientPermissionsException.

        Args:
            error (str): A message describing the validation failure for the email address.
        """
        self.error = error
        super().__init__("Insufficient permissions.")
