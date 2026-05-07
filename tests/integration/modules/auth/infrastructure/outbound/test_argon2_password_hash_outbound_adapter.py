"""This module contains tests for the Argon2PasswordHashOutboundAdapter class."""

from faker import Faker

from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)


class TestArgon2PasswordHashOutboundAdapter:
    # ---------------------------------------------------------------------------
    # Method: hash
    # ---------------------------------------------------------------------------

    def test_should_return_password_hash_when_plain_password_is_provided(
        self, faker: Faker, password_hash_outbound: Argon2PasswordHashOutboundAdapter
    ) -> None:
        """Test that the hash method returns a PasswordHashVO when a PlainPasswordVO is provided."""
        plain_password = PlainPasswordVO(faker.password())

        result = password_hash_outbound.hash(plain_password)

        assert isinstance(result, PasswordHashVO)
        assert str(result) != str(plain_password)

    def test_should_return_different_hashes_when_same_plain_password_is_hashed_twice(
        self, faker: Faker, password_hash_outbound: Argon2PasswordHashOutboundAdapter
    ) -> None:
        """Test that the hash method returns different PasswordHashVOs.

        when the same PlainPasswordVO is hashed twice.
        """
        plain_password = PlainPasswordVO(faker.password())

        hash1 = password_hash_outbound.hash(plain_password)
        hash2 = password_hash_outbound.hash(plain_password)

        assert str(hash1) != str(hash2)

    # ---------------------------------------------------------------------------
    # Method: verify
    # ---------------------------------------------------------------------------

    def test_should_a(
        self, faker: Faker, password_hash_outbound: Argon2PasswordHashOutboundAdapter
    ) -> None:
        plain_password = PlainPasswordVO(faker.password())

        password_hash = password_hash_outbound.hash(plain_password)

        result = password_hash_outbound.verify(
            plain_password=plain_password, password_hash=password_hash
        )

        assert result

    def test_should_b(
        self, faker: Faker, password_hash_outbound: Argon2PasswordHashOutboundAdapter
    ) -> None:
        original_plain_password = PlainPasswordVO(faker.password())
        wrong_plain_password = PlainPasswordVO(faker.password())

        password_hash = password_hash_outbound.hash(original_plain_password)

        result = password_hash_outbound.verify(
            plain_password=wrong_plain_password, password_hash=password_hash
        )

        assert not result
