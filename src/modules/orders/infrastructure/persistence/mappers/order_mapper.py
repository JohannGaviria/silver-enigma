"""This module contains the OrderPersistenceMapper class."""

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.infrastructure.persistence.models.order_model import (
    OrderModel,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum


class OrderPersistenceMapper:
    """Class responsible for mapping Order entities to and from SQLAlchemy models."""

    @staticmethod
    def to_entity(model: OrderModel) -> OrderEntity:
        """Map a SQLAlchemy model to an Order entity.

        Args:
            model (OrderModel): The SQLAlchemy model to map.

        Returns:
            OrderEntity: The mapped Order entity.
        """
        return OrderEntity(
            id=model.id,
            buyer_id=model.buyer_id,
            supplier_id=model.supplier_id,
            status_order=OrderStatusEnum(model.status_order),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: OrderEntity) -> OrderModel:
        """Map an Order entity to a SQLAlchemy model.

        Args:
            entity (OrderEntity): The Order entity to map.

        Returns:
            OrderModel: The mapped SQLAlchemy model.
        """
        return OrderModel(
            id=entity.id,
            buyer_id=entity.buyer_id,
            supplier_id=entity.supplier_id,
            status_order=entity.status_order.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
