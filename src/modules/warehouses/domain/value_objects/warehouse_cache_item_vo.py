"""This module contains the WarehouseCacheItemVO class."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)


@dataclass(frozen=True)
class WarehouseCacheItemVO:
    """Value object representing a warehouse cache item.

    This class is a dataclass that represents a value object that contains
    information about a warehouse. It has attributes for the warehouse's ID,
    supplier ID, name, address, and other details.

    Attributes:
        id (UUID): The ID of the warehouse.
        supplier_id (UUID): The ID of the supplier that owns the warehouse.
        name (WarehouseNameVO): The name of the warehouse.
        address (WarehouseAddressVO): The address of the warehouse.
        is_active (bool): Whether the warehouse is active or not.
        created_at (datetime): The date and time when the warehouse was created.
        updated_at (datetime): The date and time when the warehouse was last updated.
    """

    id: UUID
    supplier_id: UUID
    name: WarehouseNameVO
    address: WarehouseAddressVO
    is_active: bool
    created_at: datetime
    updated_at: datetime
