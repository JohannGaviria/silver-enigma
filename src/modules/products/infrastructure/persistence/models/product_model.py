"""This module contains the ProductModel class."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class ProductModel(BaseModel):
    """SQLAlchemy model class for the Product entity.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the product.
        supplier_id (Mapped[UUID]): The unique identifier of the supplier.
        name (Mapped[str]): The name of the product.
        description (Mapped[str]): The description of the product.
        unit_of_measure (Mapped[str]): The unit of measure of the product.
        unit_price (Mapped[Decimal]): The unit price of the product.
        is_active (Mapped[bool]): A flag indicating whether the product is active.
        created_at (Mapped[datetime]): The date and time when the product was created.
        updated_at (Mapped[datetime]): The date and time when the product was last updated.
    """

    __tablename__ = "products"

    supplier_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(nullable=False, index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, index=True)
