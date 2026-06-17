"""This module contains the exceptions for the orders."""

from uuid import UUID

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


class OrderItemsRequiredException(BaseDomainException):
    """Exception raised when no items are provided for an order."""

    def __init__(self) -> None:
        """Initialize the OrderItemsRequiredException."""
        super().__init__("No items provided for order.")


class DuplicateOrderItemsException(BaseDomainException):
    """Exception raised when duplicate items are provided for an order."""

    def __init__(self) -> None:
        """Initialize the DuplicateOrderItemsException."""
        super().__init__("Duplicate items provided for order.")


class InactiveReferencedProductException(BaseDomainException):
    """Exception raised when an inactive product is provided for an order."""

    def __init__(self, product_ids: list[UUID]) -> None:
        """Initialize the InactiveReferencedProductException.

        Args:
            product_ids (list[UUID]): A list of product IDs.
        """
        super().__init__("Inactive product provided for order.")


class ProductsFromDifferentSuppliersException(BaseDomainException):
    """Exception raised when products from different suppliers are provided for an order."""

    def __init__(self) -> None:
        """Initialize the ProductsFromDifferentSuppliersException."""
        super().__init__("Products from different suppliers provided for order.")


class InvalidReferencedProductException(BaseDomainException):
    """Exception raised when an invalid referenced product is provided for an order."""

    def __init__(self, errors: list[str]) -> None:
        """Initialize the InvalidReferencedProductException.

        Args:
            errors (list[str]): A list of error messages describing the invalid referenced product.
        """
        self.errors = errors
        super().__init__("Invalid referenced product provided for order.")
