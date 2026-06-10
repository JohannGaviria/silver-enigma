"""This module contains the ProductStockVO class."""

from dataclasses import dataclass

from src.modules.products.domain.exceptions.pagination_exception import (
    InvalidPaginationElementsException,
)
from src.modules.products.domain.value_objects.product_stock_item_vo import (
    ProductStockItemVO,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ProductStockVO(BaseValueObject):
    """Value Object representing the product stock.

    Attributes:
        products_stock (list[ProductStockItemVO]): The list of product stock items.
        page (int): The page number.
        page_size (int): The page size.
        elements (int): The number of elements.
    """

    products_stock: list[ProductStockItemVO]
    page: int
    page_size: int
    elements: int

    def _validate(self) -> None:
        """Validates the WarehouseStockVO.

        This method checks if the pagination elements are valid and raises an
        exception if they are not.

        Raises:
            InvalidPaginationElementsException: If the pagination elements are invalid.
        """
        errors: list[str] = []
        if self.page < 0:
            errors.append("Page must be greater than or equal to 0.")
        if self.page_size < 0:
            errors.append("Page size must be greater than or equal to 0.")
        if self.elements < 0:
            errors.append("Elements must be greater than or equal to 0.")

        if errors:
            raise InvalidPaginationElementsException(errors)
