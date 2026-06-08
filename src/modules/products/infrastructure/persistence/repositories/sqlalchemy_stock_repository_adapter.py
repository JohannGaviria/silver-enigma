"""This module contains the SQLAlchemyStockRepositoryAdapter class."""

from sqlite3 import IntegrityError
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.exceptions.stock_exception import (
    StockRepositoryException,
)
from src.modules.products.domain.ports.repositories.stock_repository_port import (
    StockRepositoryPort,
)
from src.modules.products.infrastructure.persistence.mappers.stock_mapper import (
    StockPersistenceMapper,
)
from src.modules.products.infrastructure.persistence.models.stock_model import (
    StockModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyStockRepositoryAdapter(StockRepositoryPort):
    """Implements StockRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyProductUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyStockRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_id(self, stock_id: UUID) -> StockEntity | None:
        """Retrieves a StockEntity by its ID.

        Args:
            stock_id (UUID): The ID of the stock to retrieve.

        Returns:
            StockEntity | None: The stock entity with the given ID, or None
                if no such stock exists.

        Raises:
            StockRepositoryException: If any other database error occurs.
        """
        try:
            stmt = select(StockModel).where(StockModel.id == stock_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return StockPersistenceMapper.to_entity(model) if model else None
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving stock.", exc_info=str(e)
            )
            raise StockRepositoryException(
                "Database error during stock retrieval."
            ) from e

    async def find_by_product_and_warehouse(
        self, product_id: UUID, warehouse_id: UUID
    ) -> StockEntity | None:
        """Retrieves a StockEntity by its product and warehouse IDs.

        Args:
            product_id (UUID): The ID of the product.
            warehouse_id (UUID): The ID of the warehouse.

        Returns:
            StockEntity | None: The stock entity with the given product and warehouse IDs, or None
                if no such stock exists.

        Raises:
            StockRepositoryException: If any other database error occurs.
        """
        try:
            stmt = select(StockModel).where(
                StockModel.product_id == product_id,
                StockModel.warehouse_id == warehouse_id,
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return StockPersistenceMapper.to_entity(model) if model else None
        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving stock.", exc_info=str(e)
            )
            raise StockRepositoryException(
                "Database error during stock retrieval."
            ) from e

    async def update(self, entity: StockEntity) -> StockEntity:
        """Update a stock entity in the repository.

        Args:
            entity (StockEntity): The stock entity to update.

        Returns:
            StockEntity: The updated stock entity.

        Raises:
            StockRepositoryException: If any other database error occurs.
        """
        try:
            model = StockPersistenceMapper.to_model(entity)
            merged_model = await self.session.merge(model)
            await self.session.flush()
            await self.session.refresh(merged_model)
            self._logger.info("Stock updated.", stock_id=str(merged_model.id))
            return StockPersistenceMapper.to_entity(merged_model)
        except IntegrityError as e:
            self._logger.error("Integrity error while updating stock.", exc_info=str(e))
            raise StockRepositoryException(
                "Stock already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving stock.", exc_info=str(e))
            raise StockRepositoryException(
                "Database error during stock creation."
            ) from e

    async def save(self, entity: StockEntity) -> StockEntity:
        """Persists a StockEntity within the current transaction and returns it.

        Args:
            entity (StockEntity): The stock entity to be saved.

        Returns:
            StockEntity: The flushed stock entity, with any server-generated
                fields (e.g. ``created_at``) populated.

        Raises:
            StockRepositoryException: If any other database error occurs.
        """
        try:
            model = StockPersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return StockPersistenceMapper.to_entity(model)
        except IntegrityError as e:
            self._logger.error("Integrity error while saving stock.", exc_info=str(e))
            raise StockRepositoryException(
                "Stock already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving stock.", exc_info=str(e))
            raise StockRepositoryException(
                "Database error during stock creation."
            ) from e
