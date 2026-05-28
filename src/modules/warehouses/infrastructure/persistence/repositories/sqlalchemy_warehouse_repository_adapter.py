"""This module contains the SQLAlchemyWarehouseRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseRepositoryException,
)
from src.modules.warehouses.domain.ports.repositories.warehouse_repository_port import (
    WarehouserRepositoryPort,
)
from src.modules.warehouses.infrastructure.persistence.mappers.warehouse_mapper import (
    WarehousePersistenceMapper,
)
from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyWarehouseRepositoryAdapter(WarehouserRepositoryPort):
    """Implements WarehouserRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyAuthUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyWarehouseRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_all_by_supplier_id(self, supplier_id: UUID) -> list[WarehouseEntity]:
        """Finds all warehouses by supplier ID within the current transaction.

        Args:
            supplier_id (UUID): The supplier ID to find warehouses for.

        Returns:
            list[WarehouseEntity]: A list of warehouse entities.

        Raises:
            WarehouseRepositoryException: If any other database error occurs.
        """
        try:
            stmt = select(WarehouseModel).where(
                WarehouseModel.supplier_id == supplier_id
            )
            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [WarehousePersistenceMapper.to_entity(model) for model in models]
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving warehouses.", exc_info=str(e)
            )
            raise WarehouseRepositoryException(
                "Database error during warehouse retrieval."
            ) from e

    async def save(self, entity: WarehouseEntity) -> WarehouseEntity:
        """Persists a WarehouseEntity within the current transaction and returns it.

        Args:
            entity (WarehouseEntity): The warehouse entity to be saved.

        Returns:
            WarehouseEntity: The flushed warehouse entity, with any server-generated
                fields (e.g. ``created_at``) populated.

        Raises:
            WarehouseRepositoryException: If any other database error occurs.
        """
        try:
            model = WarehousePersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            self._logger.info("Warehouse saved.", warehouse_id=str(model.id))
            return WarehousePersistenceMapper.to_entity(model)
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving warehouse", exc_info=str(e))
            raise WarehouseRepositoryException(
                "Database error during warehouse creation."
            ) from e
