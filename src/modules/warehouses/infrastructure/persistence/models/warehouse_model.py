"""This module contains the WarehouseModel class."""

from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.persistence.base_model import BaseModel


class WarehouseModel(BaseModel):
    """SQLAlchemy model for the Warehouse entity.

    Attributes:
        id (UUID): Unique identifier for the warehouse.
        supplier_id (UUID): The ID of the supplier that owns the warehouse.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
        is_active (bool): Whether the warehouse is active.
        created_at (datetime): Timestamp when the warehouse was created.
        updated_at (datetime): Timestamp when the warehouse was last updated.
    """

    __tablename__ = "warehouses"
    supplier_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(index=True, nullable=False)
