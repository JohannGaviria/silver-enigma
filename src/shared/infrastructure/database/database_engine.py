"""This module contains the DatabaseEngine class."""

from threading import Lock

import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings

logger = structlog.get_logger(__name__)


class DatabaseEngine:
    """Manages SQLAlchemy engine and session factory lifecycle."""

    _engine = None
    _session_factory: sessionmaker | None = None
    _lock = Lock()

    @classmethod
    def get_engine(cls) -> Engine:
        """Get or create the SQLAlchemy engine.

        Uses double-checked locking to ensure thread-safe lazy initialization.

        Returns:
            Engine: A SQLAlchemy engine instance.
        """
        if cls._engine is None:
            with cls._lock:
                if cls._engine is None:  # double-check locking
                    logger.info(
                        event="db_engine_create",
                        url=settings.DATABASE_URL,
                    )
                    cls._engine = create_engine(
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
    def get_session_factory(cls) -> sessionmaker:
        """Get or create the SQLAlchemy session factory.

        Uses double-checked locking to ensure thread-safe lazy initialization.

        Returns:
            sessionmaker: A SQLAlchemy session factory bound to the engine.
        """
        if cls._session_factory is None:
            with cls._lock:
                if cls._session_factory is None:
                    logger.debug(event="db_session_factory_create")
                    cls._session_factory = sessionmaker(
                        bind=cls.get_engine(),
                        autocommit=False,
                        autoflush=False,
                        expire_on_commit=False,
                    )
        return cls._session_factory

    @classmethod
    def create_session(cls) -> Session:
        """Create a new database session."""
        return cls.get_session_factory()()

    @classmethod
    def health_check(cls) -> bool:
        """Perform a health check by executing a simple query against the database.

        Returns:
            bool: True if the database is healthy, False otherwise.
        """
        try:
            with cls.get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug(event="db_health_ok")
            return True
        except SQLAlchemyError as exc:
            logger.error(event="db_health_fail", error=str(exc))
            cls.dispose()
            return False

    @classmethod
    def dispose(cls) -> None:
        """Dispose engine and reset state.

        Discard the motor if the status check fails to ensure that any
        obsolete or broken connections are closed and a new motor is
        created on the next attempt.
        """
        with cls._lock:
            if cls._engine:
                logger.info(event="db_engine_dispose")
                cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
