"""This module contains the OrderItemsModel class."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class OrderItemsModel(BaseModel):
    """Model representing an order item.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the order item.
        order_id (Mapped[UUID]): The ID of the order.
        product_id (Mapped[UUID]): The ID of the product.
        quantity (Mapped[int]): The quantity of the product.
        unit_price (Mapped[Decimal]): The unit price of the product.
        created_at (Mapped[datetime]): The timestamp when the order item was created.
        updated_at (Mapped[datetime]): The timestamp when the order item was last updated.
    """

    __tablename__ = "order_items"
    order_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
