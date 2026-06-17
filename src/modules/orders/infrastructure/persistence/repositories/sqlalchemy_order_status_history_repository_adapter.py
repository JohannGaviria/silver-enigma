"""This module contains the SQLAlchemyOrderStatusHistoryRepositoryAdapter class."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.entities.order_status_history_entity import (
    OrderStatusHistoryEntity,
)
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.ports.repositories.order_status_history_repository_port import (
    OrderStatusHistoryRepositoryPort,
)
from src.modules.orders.infrastructure.persistence.mappers.order_status_history_mapper import (
    OrderStatusHistoryPersistenceMapper,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyOrderStatusHistoryRepositoryAdapter(OrderStatusHistoryRepositoryPort):
    """Implements OrderStatusHistoryRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyOrderManagementUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyOrderStatusHistoryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def save(self, entity: OrderStatusHistoryEntity) -> None:
        """Persists an OrderStatusHistoryEntity within the current transaction.

        This operation must always occur within the same transaction that
        updates the parent order status, guaranteeing atomic consistency
        between the current order state and its audit trail.

        Args:
            entity (OrderStatusHistoryEntity): The order status history entity to save.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            model = OrderStatusHistoryPersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            self._logger.info(
                "Order status history saved.",
                history_id=str(model.id),
                order_id=str(model.order_id),
                new_status=str(model.new_status),
            )
        except IntegrityError as e:
            self._logger.error(
                "Integrity error while saving order status history.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Order status history already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while saving order status history.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order status history creation."
            ) from e
