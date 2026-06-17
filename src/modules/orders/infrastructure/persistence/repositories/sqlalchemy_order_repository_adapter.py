"""This module contains the SQLAlchemyOrderRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.entities.order_entity import OrderEntity
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.ports.repositories.order_repository_port import (
    OrderRepositoryPort,
)
from src.modules.orders.infrastructure.persistence.mappers.order_mapper import (
    OrderPersistenceMapper,
)
from src.modules.orders.infrastructure.persistence.models.order_model import (
    OrderModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyOrderRepositoryAdapter(OrderRepositoryPort):
    """Implements OrderRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyOrderManagementUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyOrderRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def save(self, entity: OrderEntity) -> OrderEntity:
        """Persists an OrderEntity within the current transaction and returns it.

        Args:
            entity (OrderEntity): The order entity to be saved.

        Returns:
            OrderEntity: The flushed order entity, with any server-generated
                fields (e.g. ``created_at``) populated.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            model = OrderPersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            self._logger.info("Order saved.", order_id=str(model.id))
            return OrderPersistenceMapper.to_entity(model)
        except IntegrityError as e:
            self._logger.error("Integrity error while saving order.", exc_info=str(e))
            raise OrderRepositoryException(
                "Order already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving order.", exc_info=str(e))
            raise OrderRepositoryException(
                "Database error during order creation."
            ) from e

    async def find_by_id(self, order_id: UUID) -> OrderEntity | None:
        """Retrieves an OrderEntity by its ID.

        Args:
            order_id (UUID): The ID of the order to retrieve.

        Returns:
            OrderEntity | None: The order entity with the given ID, or None
                if no such order exists.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            stmt = select(OrderModel).where(OrderModel.id == order_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return OrderPersistenceMapper.to_entity(model) if model else None
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving order.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during order retrieval."
            ) from e

    async def update(self, entity: OrderEntity) -> OrderEntity:
        """Update an order entity in the repository.

        Args:
            entity (OrderEntity): The order entity to update.

        Returns:
            OrderEntity: The updated order entity.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            model = OrderPersistenceMapper.to_model(entity)
            merged_model = await self.session.merge(model)
            await self.session.flush()
            await self.session.refresh(merged_model)
            self._logger.info("Order updated.", order_id=str(merged_model.id))
            return OrderPersistenceMapper.to_entity(merged_model)
        except IntegrityError as e:
            self._logger.error("Integrity error while updating order.", exc_info=str(e))
            raise OrderRepositoryException(
                "Order already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while updating order.", exc_info=str(e))
            raise OrderRepositoryException("Database error during order update.") from e
