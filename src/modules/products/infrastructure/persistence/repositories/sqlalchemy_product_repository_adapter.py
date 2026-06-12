"""This module contains the SQLAlchemyProductRepositoryAdapter class."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.exceptions.product_exception import (
    ProductRepositoryException,
)
from src.modules.products.domain.ports.repositories.product_repository_port import (
    ProductRepositoryPort,
)
from src.modules.products.infrastructure.persistence.mappers.product_mapper import (
    ProductPersistenceMapper,
)
from src.modules.products.infrastructure.persistence.models.product_model import (
    ProductModel,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyProductRepositoryAdapter(ProductRepositoryPort):
    """Implements ProductRepositoryPort using SQLAlchemy for database operations.

    This adapter participates in the Unit of Work pattern: it never calls
    ``session.commit()`` or ``session.rollback()`` directly. Transaction
    control is the exclusive responsibility of the
    :class:`SQLAlchemyProductUnitOfWorkAdapter` that owns the session.
    """

    def __init__(
        self, session: AsyncSession, logger_factory_outbound: LoggerFactoryOutboundPort
    ) -> None:
        """Initializes the SQLAlchemyProductRepositoryAdapter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session provided
                by the Unit of Work.
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                for creating loggers.
        """
        self.session = session
        self._logger = logger_factory_outbound.get_logger(__name__)

    async def find_by_id(self, product_id: UUID) -> ProductEntity | None:
        """Retrieves a ProductEntity by its ID.

        Args:
            product_id (UUID): The ID of the product to retrieve.

        Returns:
            ProductEntity | None: The product entity with the given ID, or None
                if no such product exists.

        Raises:
            ProductRepositoryException: If any other database error occurs.
        """
        try:
            stmt = select(ProductModel).where(ProductModel.id == product_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            return ProductPersistenceMapper.to_entity(model) if model else None

        except SQLAlchemyError as e:
            self._logger.error(
                "Database error while retrieving product.", exc_info=str(e)
            )
            raise ProductRepositoryException(
                "Database error during product retrieval."
            ) from e

    async def update(self, entity: ProductEntity) -> ProductEntity:
        """Update a product entity in the repository.

        Args:
            entity (ProductEntity): The product entity to update.

        Returns:
            ProductEntity: The updated product entity.

        Raises:
            ProductRepositoryException: If any other database error occurs.
        """
        try:
            model = ProductPersistenceMapper.to_model(entity)
            merged_model = await self.session.merge(model)
            await self.session.flush()
            await self.session.refresh(merged_model)
            self._logger.info("Product updated.", product_id=str(merged_model.id))
            return ProductPersistenceMapper.to_entity(merged_model)
        except IntegrityError as e:
            self._logger.error(
                "Integrity error while updating product.", exc_info=str(e)
            )
            raise ProductRepositoryException(
                "Product already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving product.", exc_info=str(e))
            raise ProductRepositoryException(
                "Database error during product creation."
            ) from e

    async def save(self, entity: ProductEntity) -> ProductEntity:
        """Persists a ProductEntity within the current transaction and returns it.

        Args:
            entity (ProductEntity): The product entity to be saved.

        Returns:
            ProductEntity: The flushed product entity, with any server-generated
                fields (e.g. ``created_at``) populated.

        Raises:
            ProductRepositoryException: If any other database error occurs.
        """
        try:
            model = ProductPersistenceMapper.to_model(entity)
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            return ProductPersistenceMapper.to_entity(model)
        except IntegrityError as e:
            self._logger.error("Integrity error while saving product.", exc_info=str(e))
            raise ProductRepositoryException(
                "Product already exists or violates constraints."
            ) from e
        except SQLAlchemyError as e:
            self._logger.error("Database error while saving product.", exc_info=str(e))
            raise ProductRepositoryException(
                "Database error during product creation."
            ) from e
