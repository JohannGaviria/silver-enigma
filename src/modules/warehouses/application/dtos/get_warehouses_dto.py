"""This module contains the dto's for the get warehouses use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_cache_item_vo import (
    WarehouseCacheItemVO,
)


@dataclass(frozen=True)
class WarehouseItemDto:
    """Data transfer object for a warehouse item.

    Attributes:
        id (UUID): The ID of the warehouse item.
        supplier_id (UUID): The ID of the supplier that owns the warehouse item.
        name (str): The name of the warehouse item.
        address (str): The address of the warehouse item.
        is_active (bool): Whether the warehouse item is active or not.
        created_at (datetime): The date and time when the warehouse item was created.
        updated_at (datetime): The date and time when the warehouse item was last updated.
    """

    id: UUID
    supplier_id: UUID
    name: str
    address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, warehouse: WarehouseEntity) -> "WarehouseItemDto":
        """Factory method to create a WarehouseItemDto from a WarehouseEntity.

        Args:
            warehouse (WarehouseEntity): The WarehouseEntity to create a WarehouseItemDto from.

        Returns:
            WarehouseItemDto: The created WarehouseItemDto.
        """
        return cls(
            id=warehouse.id,
            supplier_id=warehouse.supplier_id,
            name=str(warehouse.name),
            address=str(warehouse.address),
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )

    @classmethod
    def from_vo(cls, warehouse: WarehouseCacheItemVO) -> "WarehouseItemDto":
        """Factory method to create a WarehouseItemDto from a WarehouseEntity.

        Args:
            warehouse (WarehouseCacheItemVO): The WarehouseCacheItemVO
                to create a WarehouseItemDto from.

        Returns:
            WarehouseItemDto: The created WarehouseItemDto.
        """
        return cls(
            id=warehouse.id,
            supplier_id=warehouse.supplier_id,
            name=str(warehouse.name),
            address=str(warehouse.address),
            is_active=warehouse.is_active,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
        )


@dataclass(frozen=True)
class GetWarehousesResponseDto:
    """Data transfer object for a response containing a list of warehouse items.

    Attributes:
        warehouses (list[WarehouseItemDto]): A list of warehouse items.
    """

    warehouses: list[WarehouseItemDto]

    @classmethod
    def from_warehouses(
        cls,
        warehouses: list[WarehouseEntity],
    ) -> "GetWarehousesResponseDto":
        """Factory method to create a GetWarehousesResponseDto from a list of WarehouseEntity.

        Args:
            warehouses (list[WarehouseEntity]): A list of WarehouseEntity to create a GetWarehousesResponseDto from.

        Returns:
            GetWarehousesResponseDto: The created GetWarehousesResponseDto.
        """
        return cls(
            warehouses=[
                WarehouseItemDto.from_entity(warehouse) for warehouse in warehouses
            ]
        )

    @classmethod
    def from_cache_value(
        cls, warehouses: WarehouseBySupplierCacheValueVO
    ) -> "GetWarehousesResponseDto":
        """Factory method to create a GetWarehousesResponseDto from a WarehouseBySupplierCacheValueVO.

        Args:
            warehouses (WarehouseBySupplierCacheValueVO): The WarehouseBySupplierCacheValueVO to create a GetWarehousesResponseDto from.

        Returns:
            GetWarehousesResponseDto: The created GetWarehousesResponseDto.
        """
        return cls(
            warehouses=[
                WarehouseItemDto.from_vo(warehouse)
                for warehouse in warehouses.warehouses
            ]
        )
