"""This module contains the OrderStatusHistoryModel class."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class OrderStatusHistoryModel(BaseModel):
    """Model representing an order status history.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the order status history.
        order_id (Mapped[UUID]): The order ID.
        previous_status (Mapped[str]): The previous order status.
        new_status (Mapped[str]): The new order status.
        changed_by (Mapped[UUID]): The ID of the user who changed the order status.
        changed_by_role (Mapped[str]): The role of the user who changed the order status.
        created_at (Mapped[datetime]): The timestamp when the order status history was created.
        updated_at (Mapped[datetime]): The timestamp when the order status history was last updated.
    """

    __tablename__ = "orders_status_history"
    order_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    previous_status: Mapped[str] = mapped_column(nullable=False, index=True)
    new_status: Mapped[str] = mapped_column(nullable=False, index=True)
    changed_by: Mapped[UUID] = mapped_column(nullable=False, index=True)
    changed_by_role: Mapped[str] = mapped_column(nullable=False, index=True)
