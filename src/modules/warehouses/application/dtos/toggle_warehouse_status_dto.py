"""This modules contains the dto's for ToggleWarehouseUseCase class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ToggleWarehouseStatusCommandDto:
    """Command DTO for toggling the status of a warehouse.

    Attributes:
        warehouse_id (UUID): The ID of the warehouse to toggle.
        is_active (bool): Whether the warehouse should be active or not.
    """

    warehouse_id: UUID
    is_active: bool


@dataclass(frozen=True)
class ToggleWarehouseStatusResponseDto:
    """Response DTO for toggling the status of a warehouse.

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
