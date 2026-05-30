"""This module contains the WarehouseBySupplierCacheKeyVO class."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


@dataclass(frozen=True)
class WarehouseBySupplierCacheKeyVO(CacheKeyVO):
    """Value object representing the cache key for the warehouses by supplier."""

    @classmethod
    def from_supplier_id(cls, supplier_id: UUID) -> "WarehouseBySupplierCacheKeyVO":
        """Create a cache key for the warehouses by supplier using the supplier ID.

        This ensures that the cache key is unique for each supplier
        and does not expose the supplier ID itself.

        Args:
            supplier_id (UUID): The ID of the supplier for which to create the cache key.

        Returns:
            WarehouseBySupplierCacheKeyVO: An instance of the cache key
                value object for the warehouses by supplier
        """
        return cls(key=f"cache:warehouses_by_supplier:{str(supplier_id)}")
