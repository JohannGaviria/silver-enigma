"""This module contains the stock domain exceptions."""

from uuid import UUID

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidTotalStockException(BaseDomainException):
    """Exception raised when a total stock is invalid."""

    def __init__(self, errors: list[str], total_stock: int):
        """Initializes the InvalidTotalStockException.

        Args:
            errors (list[str]): A list of error messages.
            total_stock (int): The total stock of the product.
        """
        self.errors = errors
        self.total_stock = total_stock
        super().__init__("Total stock is invalid.")


class InvalidAvailableStockException(BaseDomainException):
    """Exception raised when an available stock is invalid."""

    def __init__(self, errors: list[str], available_stock: int):
        """Initializes the InvalidAvailableStockException.

        Args:
            errors (list[str]): A list of error messages.
            available_stock (int): The available stock of the product.
        """
        self.errors = errors
        self.available_stock = available_stock
        super().__init__("Available stock is invalid.")


class StockConflictException(BaseDomainException):
    """Exception raised when stock conflicts with existing stock."""

    def __init__(
        self,
        product_id: UUID,
        warehouse_id: UUID,
        requested_quantity: int,
        available_stock: int,
    ):
        """Initializes the StockConflictException.

        Args:
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.
            requested_quantity (int): The requested quantity.
            available_stock (int): The available stock.
        """
        self.product_id = product_id
        self.warehouse_id = warehouse_id
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
        super().__init__("Stock conflicts with existing stock.")
