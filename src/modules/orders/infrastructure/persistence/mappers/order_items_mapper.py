"""This module contains the OrderItemsPersistenceMapper class."""

from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO
from src.modules.orders.infrastructure.persistence.models.order_items_model import (
    OrderItemsModel,
)


class OrderItemsPersistenceMapper:
    """Class responsible for mapping OrderItems entities to and from SQLAlchemy models."""

    @staticmethod
    def to_entity(model: OrderItemsModel) -> OrderItemsEntity:
        """Map a SQLAlchemy model to an OrderItems entity.

        Args:
            model (OrderItemsModel): The SQLAlchemy model to map.

        Returns:
            OrderItemsEntity: The mapped OrderItems entity.
        """
        return OrderItemsEntity(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=QuantityVO(model.quantity),
            unit_price=model.unit_price,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: OrderItemsEntity) -> OrderItemsModel:
        """Map an OrderItems entity to a SQLAlchemy model.

        Args:
            entity (OrderItemsEntity): The OrderItems entity to map.

        Returns:
            OrderItemsModel: The mapped SQLAlchemy model.
        """
        return OrderItemsModel(
            id=entity.id,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity.value(),
            unit_price=entity.unit_price,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
