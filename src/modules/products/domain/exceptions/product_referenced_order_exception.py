"""This module contains the exception for product referenced order."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidProductReferencedOrderException(BaseDomainException):
    """Exception raised when a product is referenced by an order."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidProductReferencedOrderException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Invalid product referenced order.")


class ProductHasActiveOrdersException(BaseDomainException):
    """Exception raised when a product has active orders."""

    def __init__(self, error: str) -> None:
        """Initializes the ProductHasActiveOrdersException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Product has active orders.")
