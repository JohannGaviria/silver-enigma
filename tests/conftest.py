import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.infrastructure.persistence.base_model import Base


def pytest_configure() -> None:
    """Pytest configuration hook to load environment variables."""
    load_dotenv(".env.test", override=True)


TEST_DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://test-postgres:password@localhost:5433/test_silver_enigma",
)


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Fixture that sets up an asynchronous database engine for testing.

    Creates the schema on entry and disposes the engine on exit.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Fixture that provides an asynchronous database session for testing.

    Uses a transaction for each test to ensure isolation and rolls back after the test completes.
    """
    async with engine.connect() as connection:
        await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session

        await connection.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def faker() -> Faker:
    """Fixture that provides a Faker instance."""
    return Faker()


@pytest.fixture
def logger_factory_outbound() -> StructlogLoggerFactoryOutboundAdapter:
    return StructlogLoggerFactoryOutboundAdapter()


# ---------------------------------------------------------------------------
# Modules: AUTH
# ---------------------------------------------------------------------------


@pytest.fixture()
def password_hash() -> str:
    """Fixture that provides a hashed password for testing purposes."""
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYJXRz.HV9K"


@pytest.fixture
def password_hash_outbound() -> Argon2PasswordHashOutboundAdapter:
    """Fixture for creating an instance of Argon2PasswordHashOutboundAdapter."""
    return Argon2PasswordHashOutboundAdapter()


@pytest.fixture()
def user_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyUserRepositoryAdapter:
    """Fixture that provides an instance of SQLAlchemyUserRepositoryAdapter for testing."""
    return SQLAlchemyUserRepositoryAdapter(
        session=db_session, logger_factory_outbound=logger_factory_outbound
    )
