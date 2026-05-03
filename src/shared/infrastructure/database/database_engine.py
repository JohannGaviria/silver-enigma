"""This module contains the DatabaseEngine class."""

from threading import Lock

import structlog
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings

logger = structlog.get_logger(__name__)


class DatabaseEngine:
    """Manages SQLAlchemy async engine and session factory lifecycle.

    Consumers should interact with the database exclusively through the Unit of
    Work pattern. The recommended entry point for application code is
    :meth:`get_session_factory`, which returns the shared
    ``async_sessionmaker`` that the UoW adapters use to open per-request
    sessions.

    :meth:`create_session` is provided as a convenience for infrastructure
    utilities (health checks, CLI bootstrap) that need a one-off session
    outside of a UoW context. It must **not** be used inside use cases.
    """

    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _lock = Lock()

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Get or create the shared async SQLAlchemy engine (lazy, thread-safe).

        Returns:
            AsyncEngine: The singleton engine instance.
        """
        if cls._engine is None:
            with cls._lock:
                if cls._engine is None:
                    logger.info(
                        event="Creating async database engine.",
                        url=settings.DATABASE_URL,
                    )
                    cls._engine = create_async_engine(
                        settings.DATABASE_URL,
                        echo=False,
                        pool_pre_ping=True,
                        pool_size=10,
                        max_overflow=20,
                        pool_timeout=30,
                        pool_recycle=1800,
                    )

        return cls._engine

    @classmethod
    def get_session_factory(cls) -> async_sessionmaker[AsyncSession]:
        """Get or create the shared async session factory (lazy, thread-safe).

        This is the **canonical** way for Unit of Work adapters to obtain a
        session factory. Each UoW adapter calls the factory on ``__aenter__``
        to create an isolated ``AsyncSession`` for the duration of one
        business transaction.

        Returns:
            async_sessionmaker[AsyncSession]: The singleton session factory.
        """
        if cls._session_factory is None:
            with cls._lock:
                if cls._session_factory is None:
                    logger.debug(event="Creating async session factory.")
                    cls._session_factory = async_sessionmaker(
                        bind=cls.get_engine(),
                        class_=AsyncSession,
                        autoflush=False,
                        expire_on_commit=False,
                    )

        return cls._session_factory

    @classmethod
    def create_session(cls) -> AsyncSession:
        """Create a single one-off async database session.

        Intended only for infrastructure utilities that operate outside a Unit
        of Work context (e.g. health checks, CLI scripts). Application-layer
        use cases must never call this method directly — they must receive a
        Unit of Work through dependency injection instead.

        Returns:
            AsyncSession: A new session. The caller is responsible for closing it.
        """
        return cls.get_session_factory()()

    @classmethod
    async def health_check(cls) -> bool:
        """Perform an async connectivity health check against PostgreSQL.

        Returns:
            bool: True if the database is reachable, False otherwise.
        """
        try:
            async with cls.get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))

            logger.debug(event="Database health check passed.")
            return True

        except SQLAlchemyError as exc:
            logger.error(event="Database health check failed.", error=str(exc))
            await cls.dispose()
            return False

    @classmethod
    async def dispose(cls) -> None:
        """Dispose the engine and reset all shared state.

        Should be called on application shutdown or after an unrecoverable
        connection failure detected by the health check.
        """
        with cls._lock:
            if cls._engine:
                logger.info(event="Disposing database engine.")
                await cls._engine.dispose()

            cls._engine = None
            cls._session_factory = None
