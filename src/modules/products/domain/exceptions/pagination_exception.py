"""This module contains the pagination exception for domain-layer."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidPaginationElementsException(BaseDomainException):
    """Exception raised when invalid pagination elements are provided."""

    def __init__(self, errors: list[str]):
        """Initializes the InvalidPaginationElementsException.

        Args:
            errors (list[str]): A list of errors.
        """
        self.errors = errors
        super().__init__("Invalid pagination elements.")
