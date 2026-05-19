"""This module contains the DatabaseEngine class."""

import asyncio

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
    """Manages SQLAlchemy async engine and session factory lifecycle."""

    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_engine(cls) -> AsyncEngine:
        """Get or create the shared async SQLAlchemy engine.

        Returns:
            AsyncEngine: The singleton engine instance.
        """
        if cls._engine is None:
            async with cls._lock:
                if cls._engine is None:
                    logger.info(event="database_engine_create")

                    cls._engine = create_async_engine(
                        settings.DATABASE_URL,
                        echo=False,
                        pool_pre_ping=True,
                        pool_size=10,
                        max_overflow=20,
                        pool_timeout=30,
                        pool_recycle=1800,
                    )

                    logger.info(event="database_engine_created")

        return cls._engine

    @classmethod
    async def get_session_factory(
        cls,
    ) -> async_sessionmaker[AsyncSession]:
        """Get or create shared async session factory."""
        if cls._session_factory is None:
            engine = await cls.get_engine()

            async with cls._lock:
                if cls._session_factory is None:
                    logger.info(event="session_factory_create")

                    cls._session_factory = async_sessionmaker(
                        bind=engine,
                        class_=AsyncSession,
                        autoflush=False,
                        expire_on_commit=False,
                    )

                    logger.info(event="session_factory_created")

        return cls._session_factory

    @classmethod
    async def create_session(cls) -> AsyncSession:
        """Create a single one-off async database session.

        Returns:
            AsyncSession: A new session. The caller is responsible for closing it.
        """
        session_factory = await cls.get_session_factory()

        return session_factory()

    @classmethod
    async def health_check(cls) -> bool:
        """Perform an async connectivity health check against PostgreSQL.

        Returns:
            bool: True if the database is reachable, False otherwise.
        """
        try:
            engine = await cls.get_engine()

            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))

            logger.debug(event="database_health_ok")

            return True

        except SQLAlchemyError as exc:
            logger.error(
                event="database_health_fail",
                error=str(exc),
            )

            await cls.dispose()

            return False

    @classmethod
    async def dispose(cls) -> None:
        """Dispose the engine and reset all shared state.

        Should be called on application shutdown or after an unrecoverable
        connection failure detected by the health check.
        """
        async with cls._lock:
            if cls._engine is not None:
                logger.info(event="database_engine_dispose")

                await cls._engine.dispose()

            cls._engine = None
            cls._session_factory = None
