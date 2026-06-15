"""This module contains the exceptions for the orders."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidQuantityException(BaseDomainException):
    """Exception raised for invalid quantity."""

    def __init__(self, errors: list[str], quantity: int) -> None:
        """Initialize the InvalidQuantityException.

        Args:
            errors (list[str]): A list of error messages describing the invalid quantity.
            quantity (int): The invalid quantity.
        """
        self.errors = errors
        self.quantity = quantity
        super().__init__("Invalid quantity provided.")


class OrderRepositoryException(BaseDomainException):
    """Exception raised for errors that occur within the OrderRepository."""

    def __init__(self, error: str) -> None:
        """Initialize the OrderRepositoryException.

        Args:
            error (str): A message describing the error that occurred within the OrderRepository.
        """
        self.error = error
        super().__init__("An error occurred in the OrderRepository.")
