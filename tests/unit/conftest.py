from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture()
def logger_factory_mock() -> Mock:
    """Fixture that provides a mock logger factory for testing."""
    return Mock()


# ===============================
# Modules: AUTH
# ===============================


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
