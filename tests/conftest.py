import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, cast

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from faker import Faker
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.main import app
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO
from src.shared.infrastructure.cache.redis_connection import RedisConnection
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.outbound.pyjwt_token_outbound_adapter import (
    PyJWTTokenOutboundAdapter,
)
from src.shared.infrastructure.outbound.redis_cache_outbound_adapter import (
    RedisCacheOutboundAdapter,
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


@pytest_asyncio.fixture()
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Fixture that sets up an asynchronous database engine for testing.

    Creates the schema on entry and disposes the engine on exit.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture()
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


@pytest_asyncio.fixture()
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Fixture that provides a real async Redis client for integration tests."""
    client = Redis(
        host="localhost",
        port=6379,
        db=0,
        password="password",
        decode_responses=True,
    )

    await client.flushdb()

    yield client

    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def reset_redis_connection() -> AsyncGenerator[None, None]:
    """Reset Redis singleton between tests."""
    await RedisConnection.close()
    RedisConnection._client = None

    yield

    await RedisConnection.close()
    RedisConnection._client = None


@pytest_asyncio.fixture()
async def async_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture that provides an AsyncClient instance."""
    DatabaseEngine._session_factory = cast(
        async_sessionmaker[AsyncSession],
        lambda: db_session,
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    DatabaseEngine._session_factory = None
    DatabaseEngine._engine = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def faker() -> Faker:
    """Fixture that provides a Faker instance."""
    return Faker()


@dataclass(frozen=True)
class FakeCacheValueVO(CacheValueVO):
    value: str

    def _validate(self) -> None:
        pass

    def to_dict(self) -> dict:
        return {"value": self.value}


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


@pytest.fixture()
def logger_factory_outbound() -> StructlogLoggerFactoryOutboundAdapter:
    return StructlogLoggerFactoryOutboundAdapter()


@pytest.fixture()
def token_outbound() -> PyJWTTokenOutboundAdapter:
    return PyJWTTokenOutboundAdapter(
        access_expires_in=600,
        refresh_expires_in=259200,
        token_secret_key="5b5ca75fd14305ce3d060c43afdda2e426eb4d26d960af4341b0cc16c327c620",
        token_algorithm="HS256",
    )


@pytest_asyncio.fixture()
async def cache_outbound(
    redis_client: Redis,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> AsyncGenerator[RedisCacheOutboundAdapter, None]:
    """Fixture that provides a RedisCacheOutboundAdapter instance."""

    def factory(data: dict[str, Any]) -> dict[str, Any]:
        return data

    yield RedisCacheOutboundAdapter(
        redis_client=redis_client,
        factory=factory,
        logger_factory_outbound=logger_factory_outbound,
    )


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


@pytest.fixture()
def pinned_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyUserUnitOfWorkAdapter:
    """Provide a UoW pinned to the test ``db_session``.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.

    Args:
        db_session: The ``AsyncSession`` provided by the root conftest fixture.
        logger_factory_outbound: Structlog logger factory.

    Returns:
        SQLAlchemyUserUnitOfWorkAdapter: A UoW ready for integration assertions.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )
