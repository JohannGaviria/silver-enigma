"""This module contains the ProductReferenceOrderVO class."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.products.domain.exceptions.product_referenced_order_exception import (
    InvalidProductReferencedOrderException,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ProductReferencedOrderVO(BaseValueObject):
    """Value object for a product referenced order.

    This value object represents a product referenced order, which is a product
    that is referenced by an order.

    Attributes:
        order_id (UUID): The ID of the order that references the product.
        product_id (UUID): The ID of the product that is referenced by the order.
        order_status (OrderStatusEnum): The status of the order that references the product.
    """

    order_id: UUID
    product_id: UUID
    order_status: OrderStatusEnum

    def _validate(self) -> None:
        """Validates the product referenced order.

        The validation checks if the order ID, product ID, and order status are not None.

        Raises:
            InvalidProductReferencedOrderException: If the order ID, product ID, or order status is None.
        """
        if self.order_id is None:
            raise InvalidProductReferencedOrderException("Order ID cannot be empty.")

        if self.product_id is None:
            raise InvalidProductReferencedOrderException("Product ID cannot be empty.")

        if self.order_status is None:
            raise InvalidProductReferencedOrderException(
                "Order status cannot be empty."
            )
