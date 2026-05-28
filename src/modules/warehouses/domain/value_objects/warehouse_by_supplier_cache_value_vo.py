"""This module contains the WarehouseBySupplierCacheValueVO class."""

from dataclasses import dataclass

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_cache_item_vo import (
    WarehouseCacheItemVO,
)
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True)
class WarehouseBySupplierCacheValueVO(CacheValueVO):
    """Value object representing a warehouse by supplier cache value.

    This class is a dataclass that inherits from the CacheValueVO class. It
    represents a value object that contains a list of warehouse cache items.

    Attributes:
        warehouses (list[WarehouseCacheItemVO]): A list of warehouse cache items.
    """

    warehouses: list[WarehouseCacheItemVO]

    def to_dict(self) -> dict:
        """Converts the WarehouseBySupplierCacheValueVO to a dictionary.

        Returns:
            dict: A dictionary representation of the WarehouseBySupplierCacheValueVO.
        """
        return {
            "warehouses": [
                {
                    "id": str(warehouse.id),
                    "supplier_id": str(warehouse.supplier_id),
                    "name": str(warehouse.name),
                    "address": str(warehouse.address),
                    "is_active": warehouse.is_active,
                    "created_at": warehouse.created_at,
                    "updated_at": warehouse.updated_at,
                }
                for warehouse in self.warehouses
            ]
        }

    @classmethod
    def from_warehouses(
        cls, warehouses: list[WarehouseEntity]
    ) -> "WarehouseBySupplierCacheValueVO":
        """Creates a new WarehouseBySupplierCacheValueVO from a list of warehouse entities.

        Args:
            warehouses (list[WarehouseEntity]): A list of warehouse entities.

        Returns:
            WarehouseBySupplierCacheValueVO: A new WarehouseBySupplierCacheValueVO instance.
        """
        return cls(
            warehouses=[
                WarehouseCacheItemVO(
                    id=warehouse.id,
                    supplier_id=warehouse.supplier_id,
                    name=warehouse.name,
                    address=warehouse.address,
                    is_active=warehouse.is_active,
                    created_at=warehouse.created_at,
                    updated_at=warehouse.updated_at,
                )
                for warehouse in warehouses
            ]
        )
