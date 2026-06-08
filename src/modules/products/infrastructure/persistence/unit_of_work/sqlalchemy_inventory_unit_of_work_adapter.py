"""This module contains the SQLAlchemyInventoryUnitOfWork class."""

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.products.domain.ports.unit_of_work.inventory_unit_of_work_port import (
    InventoryUnitOfWorkPort,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_movement_repository_adapter import (
    SQLAlchemyInventoryMovementRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_stock_repository_adapter import (
    SQLAlchemyStockRepositoryAdapter,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_query_repository_adapter import (
    SQLAlchemyWarehouseQueryRepositoryAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class SQLAlchemyInventoryUnitOfWorkAdapter(InventoryUnitOfWorkPort):
    """SQLAlchemy-backed Unit of Work for the inventory module.

    Creates a fresh :class:`AsyncSession` on entry and exposes the
    ``products``, ``warehouses``, ``stocks``, and ``inventory_movements``
    repositories bound to that session. On exit it rolls back automatically
    when an unhandled exception escapes the ``async with`` block; otherwise
    callers must explicitly call ``commit()``.

    Usage::

        async with SQLAlchemyInventoryUnitOfWorkAdapter(session_factory, logger_factory) as uow:
            product = await uow.products.save(product_entity)
            await uow.commit()
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger_factory_outbound: LoggerFactoryOutboundPort,
    ) -> None:
        """Initialise the Unit of Work adapter.

        Args:
            session_factory (async_sessionmaker[AsyncSession]): Factory used to
                create a new session for each unit of work.
            logger_factory_outbound (LoggerFactoryOutboundPort): Factory for
                creating loggers used by this adapter and its repositories.
        """
        self._session_factory = session_factory
        self._logger_factory = logger_factory_outbound
        self._logger: LoggerOutboundPort = logger_factory_outbound.get_logger(__name__)
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyInventoryUnitOfWorkAdapter":
        """Open a new database session and initialise all repositories.

        Returns:
            SQLAlchemyInventoryUnitOfWorkAdapter: This instance, ready to use.
        """
        self._logger.debug("inventory unit of work: begin transaction")
        self._session = self._session_factory()
        self.products = SQLAlchemyProductRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.warehouses = SQLAlchemyWarehouseQueryRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.stocks = SQLAlchemyStockRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.inventory_movements = SQLAlchemyInventoryMovementRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the session, rolling back if an exception escaped the block.

        Args:
            exc_type: The exception class, if any.
            exc_val: The exception instance, if any.
            exc_tb: The traceback, if any.
        """
        if exc_type is not None:
            self._logger.warning(
                "inventory unit of work: unhandled exception — rolling back",
                exc_type=str(exc_type),
            )
            await self.rollback()

        if self._session is not None:
            await self._session.close()
            self._logger.debug("inventory unit of work: session closed")

    async def commit(self) -> None:
        """Flush and commit the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyInventoryUnitOfWorkAdapter.commit() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("inventory unit of work: commit")
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyInventoryUnitOfWorkAdapter.rollback() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("inventory unit of work: rollback")
        await self._session.rollback()
