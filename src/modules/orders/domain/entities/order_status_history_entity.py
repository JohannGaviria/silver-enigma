"""This module contains the OrderStatusHistoryEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True)
class OrderStatusHistoryEntity(BaseEntity):
    """Entity representing an order status history.

    Attributes:
        id (UUID): The unique identifier of the order status history.
        order_id (UUID): The order ID.
        previous_status (OrderStatusEnum): The previous order status.
        new_status (OrderStatusEnum): The new order status.
        changed_by (UUID): The ID of the user who changed the order status.
        changed_by_role (UserRoleEnum): The role of the user who changed the order status.
        created_at (datetime): The timestamp when the order status history was created.
        updated_at (datetime): The timestamp when the order status history was last updated.
    """

    order_id: UUID
    previous_status: OrderStatusEnum
    new_status: OrderStatusEnum
    changed_by: UUID
    changed_by_role: UserRoleEnum

    @classmethod
    def create(
        cls,
        order_id: UUID,
        previous_status: OrderStatusEnum,
        new_status: OrderStatusEnum,
        changed_by: UUID,
        changed_by_role: UserRoleEnum,
    ) -> "OrderStatusHistoryEntity":
        """Factory method to create a new OrderStatusHistoryEntity instance.

        Args:
            order_id (UUID): The ID of the order.
            previous_status (OrderStatusEnum): The previous order status.
            new_status (OrderStatusEnum): The new order status.
            changed_by (UUID): The ID of the user who changed the order status.
            changed_by_role (UserRoleEnum): The role of the user who changed the order status.

        Returns:
            OrderStatusHistoryEntity: A new OrderStatusHistoryEntity instance.
        """
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            order_id=order_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
            created_at=now,
            updated_at=now,
        )
