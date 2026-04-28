from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.infrastructure.persistence.base_model import Base

TEST_DATABASE_URL = (
    "postgresql+asyncpg://test-postgres:password@localhost:5433/test_silver_enigma"
)


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Fixture that sets up an asynchronous database engine for testing.

    This fixture creates an asynchronous engine using the specified database URL,
    initializes the database schema, and yields the engine for use in tests.
    After the tests are completed, it disposes of the engine to clean up resources.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Fixture that provides an asynchronous database session for testing.

    This fixture creates a new asynchronous session for each test, using a nested transaction
    to ensure that any changes made to the database during the test are rolled back afterward.
    """
    async with engine.connect() as connection:
        transaction = await connection.begin()

        Session = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with Session() as session:
            await session.begin_nested()

            yield session

            await session.rollback()

        await transaction.rollback()


@pytest.fixture
def faker() -> Faker:
    """Fixture that provides a Faker instance."""
    return Faker()


@pytest.fixture
def logger_factory_outbound() -> StructlogLoggerFactoryOutboundAdapter:
    return StructlogLoggerFactoryOutboundAdapter()


# ===============================
# Modules: AUTH
# ===============================


@pytest.fixture()
def password_hash() -> str:
    """Fixture that provides a hashed password for testing purposes."""
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYJXRz.HV9K"


@pytest.fixture()
def user_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyUserRepositoryAdapter:
    """Fixture that provides an instance of SQLAlchemyUserRepositoryAdapter for testing."""
    return SQLAlchemyUserRepositoryAdapter(
        session=db_session, logger_factory_outbound=logger_factory_outbound
    )
