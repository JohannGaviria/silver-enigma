"""This module contains the SQLAlchemyWarehouseQueryRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.ports.repositories.warehouse_query_repository_port import (
    WarehouseQueryRepositoryPort,
)
from src.modules.products.domain.value_objects.referenced_warehouse_vo import (
    ReferencedWarehouseVO,
)
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseRepositoryException,
)
from src.modules.warehouses.infrastructure.persistence.models.warehouse_model import (
    WarehouseModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyWarehouseQueryRepositoryAdapter(WarehouseQueryRepositoryPort):
    """Implements WarehouseQueryRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyProductUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyWarehouseQueryRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_id(self, warehouse_id: UUID) -> ReferencedWarehouseVO | None:
        """Retrieves a WarehouseEntity by its ID.

        Args:
            warehouse_id (UUID): The ID of the warehouse to retrieve.

        Returns:
            WarehouseEntity | None: The warehouse entity with the given ID, or None
                if no such warehouse exists.

        Raises:
            WarehouseRepositoryException: If any other database error occurs.
        """
        try:
            stmt = select(WarehouseModel).where(WarehouseModel.id == warehouse_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return (
                ReferencedWarehouseVO(
                    warehouse_id=model.id,
                    supplier_id=model.supplier_id,
                    is_active=model.is_active,
                )
                if model
                else None
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving warehouse.", exc_info=str(e)
            )
            raise WarehouseRepositoryException(
                "Database error during warehouse retrieval."
            ) from e
