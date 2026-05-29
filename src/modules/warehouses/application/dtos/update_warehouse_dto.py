"""This module contains the dto's for UpdateWarehouseUseCase class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UpdateWarehouseCommandDto:
    """Command DTO for updating a warehouse.

    Attributes:
        warehouse_id (UUID): The ID of the warehouse to update.
        name (str | None): The new name of the warehouse. Defaults to None.
        address (str | None): The new address of the warehouse. Defaults to None.
    """

    warehouse_id: UUID
    name: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class UpdateWarehouseResponseDto:
    """Response DTO for updating a warehouse.

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
    supplier_id: UUID
    name: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
