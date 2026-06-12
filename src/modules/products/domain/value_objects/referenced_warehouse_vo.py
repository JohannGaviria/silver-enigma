"""This module contains the ReferencedWarehouseVO class."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.products.domain.exceptions.inventory_warehouse_exception import (
    InvalidReferencedWarehouseException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class ReferencedWarehouseVO(BaseValueObject):
    """Value object representing a referenced warehouse.

    Attributes:
        warehouse_id (UUID): The ID of the warehouse.
        supplier_id (UUID): The ID of the supplier.
        is_active (bool): Whether the warehouse is active.
    """

    warehouse_id: UUID
    supplier_id: UUID
    is_active: bool

    def _validate(self) -> None:
        """Validates the value object.

        Raises:
            InvalidReferencedWarehouseException: If the warehouse ID is invalid.
        """
        if self.warehouse_id is None:
            raise InvalidReferencedWarehouseException(
                errors=["Warehouse ID cannot be None."],
                warehouse_id=self.warehouse_id,
            )

        if self.supplier_id is None:
            raise InvalidReferencedWarehouseException(
                errors=["Supplier ID cannot be None."],
                warehouse_id=self.warehouse_id,
            )

        if self.is_active is None:
            raise InvalidReferencedWarehouseException(
                errors=["Is active cannot be None."],
                warehouse_id=self.warehouse_id,
            )
