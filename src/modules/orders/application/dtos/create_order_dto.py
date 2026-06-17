"""This module contains the dto's for create order use case."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.shared.domain.enums.order_status_enum import OrderStatusEnum


@dataclass(frozen=True)
class ProductItemsDto:
    """DTO representing a product item in an order.

    Attributes:
        product_id (UUID): The ID of the product.
        quantity (int): The quantity of the product.
    """

    product_id: UUID
    quantity: int


@dataclass(frozen=True)
class ProductDetailsDto(ProductItemsDto):
    """DTO representing a product details in an order.

    Attributes:
        product_id (UUID): The ID of the product.
        quantity (int): The quantity of the product.
        name (str): The name of the product.
        unit_price (Decimal): The unit price of the product.
    """

    name: str
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderCommandDto:
    """DTO representing the command to create an order.

    Attributes:
        items (list[ProductItemsDto]): A list of product items in the order.
    """

    items: list[ProductItemsDto]


@dataclass(frozen=True)
class CreateOrderResponseDto:
    """DTO representing the response to create an order.

    Attributes:
        id (UUID): The ID of the order.
        buyer_id (UUID): The ID of the buyer.
        items (list[ProductDetailsDto]): A list of product details in the order.
        status (OrderStatusEnum): The status of the order.
        created_at (datetime): The timestamp when the order was created.
        updated_at (datetime): The timestamp when the order was last updated.
    """

    id: UUID
    buyer_id: UUID
    items: list[ProductDetailsDto]
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime
