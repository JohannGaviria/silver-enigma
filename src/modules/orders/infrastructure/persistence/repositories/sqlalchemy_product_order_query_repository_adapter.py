"""This module contains the SQLAlchemyProductOrderQueryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.infrastructure.persistence.models.order_items_model import (
    OrderItemsModel,
)
from src.modules.orders.infrastructure.persistence.models.order_model import OrderModel
from src.modules.products.domain.ports.repositories.product_order_query_repository_port import (
    ProductOrderQueryRepositoryPort,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyProductOrderQueryRepositoryAdapter(ProductOrderQueryRepositoryPort):
    """Implements ProductOrderQueryRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyAuthUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyProductOrderQueryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def exists_by_product_id_and_statuses(
        self, product_id: UUID, statuses: set[OrderStatusEnum]
    ) -> bool:
        """Check if an order exists by product ID and statuses.

        Args:
            product_id (UUID): The ID of the product.
            statuses (set[OrderStatusEnum]): The set of statuses to check.

        Returns:
            bool: True if the order exists, False otherwise.
        """
        try:
            stmt = (
                select(OrderModel.id)
                .join(OrderItemsModel, OrderItemsModel.order_id == OrderModel.id)
                .where(
                    OrderItemsModel.product_id == product_id,
                    OrderModel.status_order.in_(statuses),
                )
                .limit(1)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving order.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order retrieval."
            ) from e
