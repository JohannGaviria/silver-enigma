"""This module contains the product domain exceptions."""

from decimal import Decimal

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidProductNameException(BaseDomainException):
    """Exception raised when a product name is invalid."""

    def __init__(self, errors: list[str], name: str):
        """Initializes the InvalidProductNameException.

        Args:
            errors (list[str]): A list of error messages.
            name (str): The name of the product.
        """
        self.errors = errors
        self.name = name
        super().__init__("Product name is invalid.")


class InvalidUnitPriceException(BaseDomainException):
    """Exception raised when a unit price is invalid."""

    def __init__(self, errors: list[str], price: Decimal):
        """Initializes the InvalidUnitPriceException.

        Args:
            errors (list[str]): A list of error messages.
            price (Decimal): The unit price of the product.
        """
        self.errors = errors
        self.price = price
        super().__init__("Unit price is invalid.")


class ProductRepositoryException(BaseDomainException):
    """Exception raised when a product repository operation fails."""

    def __init__(self, error: str):
        """Initializes the ProductRepositoryException.

        Args:
            error (str): The error message.
        """
        self.error = error
        super().__init__("Product repository error.")
