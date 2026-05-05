from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

# ---------------------------------------------------------------------------
# SHARED
# ---------------------------------------------------------------------------


@pytest.fixture()
def logger_factory_mock() -> Mock:
    """Fixture that provides a mock logger factory for testing."""
    return Mock()


@pytest.fixture()
def token() -> str:
    """Fixture that provides a valid token string for testing purposes."""
    return "valid-token-123"


@pytest.fixture()
def access_token_type() -> list[str]:
    """Fixture that provides a list of valid access token types for testing."""
    return ["Bearer"]


# ---------------------------------------------------------------------------
# Modules: AUTH
# ---------------------------------------------------------------------------


@pytest.fixture()
def password_hash() -> str:
    """Fixture that provides a hashed password for testing purposes."""
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYJXRz.HV9K"


@pytest.fixture()
def user_repository_mock() -> AsyncMock:
    """Fixture that provides a mock user repository for testing."""
    return AsyncMock()


@pytest.fixture()
def password_hash_outbound_mock() -> Mock:
    """Fixture that provides a mock password hash outbound adapter for testing."""
    return Mock()


@pytest.fixture()
def session_mock() -> AsyncMock:
    """Return an ``AsyncMock`` that behaves like an ``AsyncSession``."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture()
def session_factory_mock(session_mock: AsyncMock) -> MagicMock:
    """Return a callable mock that always yields ``session_mock`` when called."""
    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value = session_mock
    return factory


@pytest.fixture()
def uow_with_session_mock(
    session_factory_mock: MagicMock,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]:
    """Provide a UoW wired to a mocked session, plus the session mock itself.

    Returns:
        tuple: ``(uow, session_mock)`` so tests can assert on both objects.
    """
    uow = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=session_factory_mock,
        logger_factory_outbound=logger_factory_outbound,
    )
    return uow, session_factory_mock.return_value


@pytest.fixture()
def user_uow_mock() -> MagicMock:
    """Build a Unit-of-Work mock that behaves as an async context manager.

    The returned mock exposes ``uow.users`` (an ``AsyncMock``) with
    ``exists_by_role`` returning ``False`` by default and ``save``
    configured to return the entity it receives.

    Returns:
        MagicMock: A UoW mock ready to be injected into the use case.
    """
    users_mock = AsyncMock()
    users_mock.exists_by_role.return_value = False
    users_mock.save.side_effect = lambda entity: entity

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)
    uow_mock.users = users_mock
    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock
