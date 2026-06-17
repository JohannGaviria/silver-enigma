"""This module contains the SQLAlchemyOrderItemsRepositoryAdapter class."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.entities.order_items_entity import OrderItemsEntity
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.ports.repositories.order_items_repository_port import (
    OrderItemsRepositoryPort,
)
from src.modules.orders.infrastructure.persistence.mappers.order_items_mapper import (
    OrderItemsPersistenceMapper,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyOrderItemsRepositoryAdapter(OrderItemsRepositoryPort):
    """Implements OrderItemsRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyOrderManagementUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyOrderItemsRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def save_many(self, entities: list[OrderItemsEntity]) -> None:
        """Save multiple order items entities within the current transaction.

        Args:
            entities (list[OrderItemsEntity]): The order items entities to save.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            models = [
                OrderItemsPersistenceMapper.to_model(entity) for entity in entities
            ]
            self.session.add_all(models)
            await self.session.flush()
            for model in models:
                await self.session.refresh(model)
            self._logger.info("Order items saved.", count=len(models))
        except IntegrityError as e:
            self._logger.error(
                "Integrity error while saving order items.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Order items already exist or violate constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while saving order items.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order items creation."
            ) from e
