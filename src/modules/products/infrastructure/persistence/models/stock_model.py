"""This module contains the StockModel class."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class StockModel(BaseModel):
    """Model representing a stock item.

    Attributes:
        id (UUID): The ID of the stock.
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        total_stock (int): The total number of items in stock.
        reserved_stock (int): The number of items reserved for purchase.
        created_at (datetime): The date and time the stock was created.
        updated_at (datetime): The date and time the stock was updated.
    """

    __tablename__ = "stocks"

    product_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    warehouse_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    total_stock: Mapped[int] = mapped_column(nullable=False)
    reserved_stock: Mapped[int] = mapped_column(nullable=False)
