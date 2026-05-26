"""This module contains the WarehouseEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.shared.domain.entities.base_entity import BaseEntity


@dataclass(frozen=True)
class WarehouseEntity(BaseEntity):
    """Entity representing a warehouse.

    Attributes:
        supplier_id (UUID): The ID of the supplier.
        name (WarehouseNameVO): The name of the warehouse.
        address (WarehouseAddressVO): The address of the warehouse.
        is_active (bool): Whether the warehouse is active or not.
    """

    supplier_id: UUID
    name: WarehouseNameVO
    address: WarehouseAddressVO
    is_active: bool

    @classmethod
    def create(
        cls,
        supplier_id: UUID,
        name: WarehouseNameVO,
        address: WarehouseAddressVO,
    ) -> "WarehouseEntity":
        """Factory method to create a new WarehouseEntity.

        This method generates a new UUID for the warehouse, sets the created_at and updated_at
        timestamps to the current time in UTC, and returns a new instance of WarehouseEntity
        with the provided supplier_id, name, and address.

        Args:
            supplier_id (UUID): The ID of the supplier.
            name (WarehouseNameVO): The name of the warehouse.
            address (WarehouseAddressVO): The address of the warehouse.

        Returns:
            WarehouseEntity: The created WarehouseEntity.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            supplier_id=supplier_id,
            name=name,
            address=address,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
