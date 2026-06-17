"""This module contains the OrderStatusHistoryPersistenceMapper class."""

from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.modules.orders.infrastructure.persistence.models.order_status_history_model import (
    OrderStatusHistoryModel,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class OrderStatusHistoryPersistenceMapper:
    """Class responsible for mapping OrderStatusHistory entities to and from SQLAlchemy models."""

    @staticmethod
    def to_entity(model: OrderStatusHistoryModel) -> OrderStatusHistoryEntity:
        """Map a SQLAlchemy model to an OrderStatusHistory entity.

        Args:
            model (OrderStatusHistoryModel): The SQLAlchemy model to map.

        Returns:
            OrderStatusHistoryEntity: The mapped OrderStatusHistory entity.
        """
        return OrderStatusHistoryEntity(
            id=model.id,
            order_id=model.order_id,
            previous_status=OrderStatusEnum(model.previous_status),
            new_status=OrderStatusEnum(model.new_status),
            changed_by=model.changed_by,
            changed_by_role=UserRoleEnum(model.changed_by_role),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: OrderStatusHistoryEntity) -> OrderStatusHistoryModel:
        """Map an OrderStatusHistory entity to a SQLAlchemy model.

        Args:
            entity (OrderStatusHistoryEntity): The OrderStatusHistory entity to map.

        Returns:
            OrderStatusHistoryModel: The mapped SQLAlchemy model.
        """
        return OrderStatusHistoryModel(
            id=entity.id,
            order_id=entity.order_id,
            previous_status=entity.previous_status.value,
            new_status=entity.new_status.value,
            changed_by=entity.changed_by,
            changed_by_role=entity.changed_by_role.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
