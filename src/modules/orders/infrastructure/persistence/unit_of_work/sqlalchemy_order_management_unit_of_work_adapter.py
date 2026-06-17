"""This module contains the SQLAlchemyOrderManagementUnitOfWorkAdapter class."""

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.orders.domain.ports.unit_of_work.order_management_unit_of_work_port import (
    OrderManagementUnitOfWorkPort,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_items_repository_adapter import (
    SQLAlchemyOrderItemsRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_status_history_repository_adapter import (
    SQLAlchemyOrderStatusHistoryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_query_repository_adapter import (
    SQLAlchemyProductQueryRepositoryAdapter,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.ports.outbound.logger_outbound_port import LoggerOutboundPort


class SQLAlchemyOrderManagementUnitOfWorkAdapter(OrderManagementUnitOfWorkPort):
    """SQLAlchemy-backed Unit of Work for the order management module.

    Creates a fresh :class:`AsyncSession` on entry and exposes the
    ``orders``, ``order_items``, ``orders_status_history``, and
    ``product_query`` repositories bound to that session.

    On exit it rolls back automatically when an unhandled exception escapes
    the ``async with`` block; otherwise callers must explicitly call
    ``commit()``.

    Usage::

        async with SQLAlchemyOrderManagementUnitOfWorkAdapter(session_factory, logger_factory) as uow:
            order = await uow.orders.save(order_entity)
            await uow.orders_status_history.save(history_entity)
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

    async def __aenter__(self) -> "SQLAlchemyOrderManagementUnitOfWorkAdapter":
        """Open a new database session and initialise all repositories.

        Returns:
            SQLAlchemyOrderManagementUnitOfWorkAdapter: This instance, ready to use.
        """
        self._logger.debug("order management unit of work: begin transaction")
        self._session = self._session_factory()
        self.orders = SQLAlchemyOrderRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.order_items = SQLAlchemyOrderItemsRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.orders_status_history = SQLAlchemyOrderStatusHistoryRepositoryAdapter(
            session=self._session,
            logger_factory_outbound=self._logger_factory,
        )
        self.product_query = SQLAlchemyProductQueryRepositoryAdapter(
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
                "order management unit of work: unhandled exception — rolling back",
                exc_type=str(exc_type),
            )
            await self.rollback()

        if self._session is not None:
            await self._session.close()
            self._logger.debug("order management unit of work: session closed")

    async def commit(self) -> None:
        """Flush and commit the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyOrderManagementUnitOfWorkAdapter.commit() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("order management unit of work: commit")
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction.

        Raises:
            RuntimeError: If called outside an ``async with`` block.
        """
        if self._session is None:
            raise RuntimeError(
                "SQLAlchemyOrderManagementUnitOfWorkAdapter.rollback() called outside "
                "of an 'async with' block."
            )
        self._logger.debug("order management unit of work: rollback")
        await self._session.rollback()
