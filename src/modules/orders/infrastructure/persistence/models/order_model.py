"""This module contains the OrderModel class."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class OrderModel(BaseModel):
    """Model representing an order.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the order.
        buyer_id (Mapped[UUID]): The ID of the buyer.
        supplier_id (Mapped[UUID]): The ID of the supplier.
        warehouse_id (Mapped[UUID]): The ID of the warehouse.
        status_order (Mapped[str]): The order status.
        created_at (Mapped[datetime]): The timestamp when the order was created.
        updated_at (Mapped[datetime]): The timestamp when the order was last updated.
    """

    __tablename__ = "orders"
    buyer_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    supplier_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    status_order: Mapped[str] = mapped_column(nullable=False, index=True)
