"""This module contains the exceptions for the orders."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class OrderRepositoryException(BaseDomainException):
    """Exception raised for errors that occur within the OrderRepository."""

    def __init__(self, error: str) -> None:
        """Initialize the OrderRepositoryException.

        Args:
            error (str): A message describing the error that occurred within the OrderRepository.
        """
        self.error = error
        super().__init__("An error occurred in the OrderRepository.")
