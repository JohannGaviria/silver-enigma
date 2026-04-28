import pytest

from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)


@pytest.fixture
def password_hash_outbound() -> Argon2PasswordHashOutboundAdapter:
    """Fixture for creating an instance of Argon2PasswordHashOutboundAdapter."""
    return Argon2PasswordHashOutboundAdapter()
