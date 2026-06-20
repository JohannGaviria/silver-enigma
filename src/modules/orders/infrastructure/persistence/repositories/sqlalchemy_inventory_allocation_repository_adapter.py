"""This module contains the SQLAlchemyInventoryAllocationRepositoryAdapter class."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.domain.entities.inventory_allocation_entity import (
    InventoryAllocationEntity,
)
from src.modules.orders.domain.exceptions.order_exception import (
    OrderRepositoryException,
)
from src.modules.orders.domain.ports.repositories.inventory_allocation_repository_port import (
    InventoryAllocationRepositoryPort,
)
from src.modules.orders.infrastructure.persistence.mappers.inventory_allocation_mapper import (
    InventoryAllocationPersistenceMapper,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyInventoryAllocationRepositoryAdapter(InventoryAllocationRepositoryPort):
    """Implements InventoryAllocationRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the Unit of Work adapter
    that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyInventoryAllocationRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def save_many(self, entities: list[InventoryAllocationEntity]) -> None:
        """Save multiple inventory allocation entities within the current transaction.

        Args:
            entities (list[InventoryAllocationEntity]): The inventory allocation entities to save.

        Raises:
            OrderRepositoryException: If any database error occurs.
        """
        try:
            models = [
                InventoryAllocationPersistenceMapper.to_model(entity)
                for entity in entities
            ]
            self.session.add_all(models)
            await self.session.flush()
            for model in models:
                await self.session.refresh(model)
            self._logger.info("Inventory allocations saved.", count=len(models))
        except IntegrityError as e:
            self._logger.error(
                "Integrity error while saving inventory allocations.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Inventory allocations already exist or violate constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while saving inventory allocations.", exc_info=str(e)
            )
            raise OrderRepositoryException(
                "Database error during inventory allocation creation."
            ) from e
