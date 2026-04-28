from unittest.mock import AsyncMock, Mock

import pytest

# ===============================
# Modules: AUTH
# ===============================


@pytest.fixture()
def password_hash() -> str:
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYJXRz.HV9K"


@pytest.fixture()
def user_repository_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def password_hash_outbound_mock() -> Mock:
    return Mock()
