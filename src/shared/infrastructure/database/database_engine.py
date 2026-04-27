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
    """Manages SQLAlchemy async engine and session factory lifecycle."""

    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _lock = Lock()

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Get or create async SQLAlchemy engine."""
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
        """Get or create async session factory."""
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
        """Create a new async database session."""
        return cls.get_session_factory()()

    @classmethod
    async def health_check(cls) -> bool:
        """Perform async health check."""
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
        """Dispose engine and reset state."""
        with cls._lock:
            if cls._engine:
                logger.info(event="Disposing database engine.")
                await cls._engine.dispose()

            cls._engine = None
            cls._session_factory = None
