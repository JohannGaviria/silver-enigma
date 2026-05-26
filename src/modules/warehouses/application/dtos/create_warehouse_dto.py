"""This module contains the dto's for the create warehouse."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BaseCreateWarehouseDto:
    """Base DTO for creating a warehouse.

    Attributes:
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
    """

    supplier_id: UUID
    name: str
    address: str


@dataclass(frozen=True)
class CreateWarehouseCommandDto(BaseCreateWarehouseDto):
    """Command DTO for creating a warehouse.

    Attributes:
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
    """

    ...


@dataclass(frozen=True)
class CreateWarehouseResponseDto(BaseCreateWarehouseDto):
    """Response DTO for creating a warehouse.

    Attributes:
        id (UUID): The ID of the warehouse.
        supplier_id (UUID): The ID of the supplier.
        name (str): The name of the warehouse.
        address (str): The address of the warehouse.
        is_active (bool): Whether the warehouse is active or not.
        created_at (datetime): The timestamp when the warehouse was created.
        updated_at (datetime): The timestamp when the warehouse was last updated.
    """

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
