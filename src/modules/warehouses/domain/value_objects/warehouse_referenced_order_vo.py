"""This module contains the WarehouseReferencedOrderVO class."""

from dataclasses import dataclass
from uuid import UUID

from src.modules.warehouses.domain.exceptions.warehouse_referenced_order_exception import (
    InvalidWarehouseReferencedOrderException,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class WarehouseReferencedOrderVO(BaseValueObject):
    """Value object representing a warehouse referenced order.

    Attributes:
        order_id (UUID): The ID of the order.
        warehouse_id (UUID): The ID of the warehouse.
        order_status (OrderStatusEnum): The order status.
    """

    order_id: UUID
    warehouse_id: UUID
    order_status: OrderStatusEnum

    def _validate(self) -> None:
        """Validate the referenced order value object.

        The validation checks if the attributes are not None and if they are valid.

        Raises:
            InvalidWarehouseReferencedOrderException: If any of the attributes are invalid.
        """
        if self.order_id is None:
            raise InvalidWarehouseReferencedOrderException("order_id cannot be empty.")

        if self.warehouse_id is None:
            raise InvalidWarehouseReferencedOrderException(
                "warehouse_id cannot be empty."
            )

        if self.order_status is None:
            raise InvalidWarehouseReferencedOrderException(
                "order_status cannot be empty."
            )
