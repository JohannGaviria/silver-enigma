"""This module contains the SQLAlchemyWarehouseUnitOfWorkAdapter class."""

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.warehouses.domain.ports.unit_of_work.warehouse_unit_of_work_port import (
    WarehouseUnitOfWorkPort,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class SQLAlchemyWarehouseUnitOfWorkAdapter(WarehouseUnitOfWorkPort):
    """SQLAlchemy-backed Unit of Work for the warehouse module.

    Creates a fresh :class:`AsyncSession` on entry and exposes the
    ``warehouses`` repository bound to that session. On exit it rolls back
    automatically when an unhandled exception escapes the ``async with``
    block; otherwise callers must explicitly call ``commit()``.

    Usage::

        async with SQLAlchemyWarehouseUnitOfWorkAdapter(session_factory, logger_factory) as uow:
            warehouse = await uow.warehouses.save(warehouse_entity)
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
        self._logger = logger_factory_outbound.get_logger(__name__)
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyWarehouseUnitOfWorkAdapter":
        """Open a new database session and initialise all repositories.

        Returns:
            SQLAlchemyWarehouseUnitOfWorkAdapter: This instance, ready to use.
        """
        self._logger.debug("warehouse unit of work: begin transaction")
        self._session = self._session_factory()
        self.warehouses = SQLAlchemyWarehouseRepositoryAdapter(
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
            exc_type (type[BaseException] | None): The exception class, if any.
            exc_val (BaseException | None): The exception instance, if any.
            exc_tb (TracebackType | None): The traceback, if any.
        """
        if exc_type is not None:
            self._logger.warning(
                "warehouse unit of work: unhandled exception — rolling back",
                exc_type=str(exc_type),
            )
            await self.rollback()

        if self._session is not None:
            await self._session.close()
            self._logger.debug("warehouse unit of work: session closed")

    async def commit(self) -> None:
        """Flush and commit the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyWarehouseUnitOfWorkAdapter.commit() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("warehouse unit of work: commit")
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyWarehouseUnitOfWorkAdapter.rollback() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("warehouse unit of work: rollback")
        await self._session.rollback()
