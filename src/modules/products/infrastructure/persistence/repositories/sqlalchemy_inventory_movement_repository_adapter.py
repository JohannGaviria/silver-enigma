"""This module contains the SQLAlchemyInventoryMovementRepositoryAdapter class."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.entities.inventory_movement_entity import (
    InventoryMovementEntity,
)
from src.modules.products.domain.exceptions.inventory_movement_exception import (
    InventoryMovementRepositoryException,
)
from src.modules.products.domain.ports.repositories.inventory_movement_repository_port import (
    InventoryMovementRepositoryPort,
)
from src.modules.products.infrastructure.persistence.mappers.inventory_movement_mapper import (
    InventoryMovementPersistenceMapper,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyInventoryMovementRepositoryAdapter(InventoryMovementRepositoryPort):
    """Implements InventoryMovementRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyProductUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyInventoryMovementRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def save(self, entity: InventoryMovementEntity) -> None:
        """Saves an InventoryMovementEntity to the repository.

        Args:
            entity (InventoryMovementEntity): The InventoryMovementEntity to be saved.

        Returns:
            None
        """
        try:
            model = InventoryMovementPersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            self._logger.info("Inventory movement saved.", movement_id=str(model.id))
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while saving inventory movement.", exc_info=str(e)
            )
            raise InventoryMovementRepositoryException(
                "Database error during inventory movement creation."
            ) from e
