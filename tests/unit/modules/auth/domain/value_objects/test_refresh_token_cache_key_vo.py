import hashlib

import pytest
from faker import Faker

from src.modules.auth.domain.value_objects.refresh_token_cache_key_vo import (
    RefreshTokenCacheKeyVO,
)
from src.shared.domain.exceptions.exception import InvalidCacheKeyException
from src.shared.domain.value_objects.token_vo import TokenVO


class TestRefreshTokenCacheKeyVO:
    def test_should_create_refresh_token_cache_key_from_token(
        self,
        faker: Faker,
    ) -> None:
        """Test that a valid cache key is created from a token."""
        token = TokenVO(faker.sha256())

        refresh_token_cache_key_vo = RefreshTokenCacheKeyVO.from_token(token)

        expected_hash = hashlib.sha256(str(token).encode()).hexdigest()

        assert refresh_token_cache_key_vo.key == (
            f"cache:refresh_token:{expected_hash}"
        )

    def test_should_generate_same_key_for_same_token(
        self,
        faker: Faker,
    ) -> None:
        """Test that the same token generates the same cache key."""
        token = TokenVO(faker.sha256())

        first = RefreshTokenCacheKeyVO.from_token(token)
        second = RefreshTokenCacheKeyVO.from_token(token)

        assert first.key == second.key

    def test_should_generate_different_keys_for_different_tokens(
        self,
        faker: Faker,
    ) -> None:
        """Test that different tokens generate different cache keys."""
        first_token = TokenVO(faker.sha256())
        second_token = TokenVO(faker.sha256())

        first = RefreshTokenCacheKeyVO.from_token(first_token)
        second = RefreshTokenCacheKeyVO.from_token(second_token)

        assert first.key != second.key

    def test_should_create_valid_cache_key_format(
        self,
        faker: Faker,
    ) -> None:
        """Test that the generated cache key follows the expected format."""
        token = TokenVO(faker.sha256())

        refresh_token_cache_key_vo = RefreshTokenCacheKeyVO.from_token(token)

        assert refresh_token_cache_key_vo.key.startswith("cache:refresh_token:")

    def test_should_raise_exception_when_cache_key_is_empty(
        self,
    ) -> None:
        """Test that an exception is raised when cache key is empty."""
        with pytest.raises(InvalidCacheKeyException):
            RefreshTokenCacheKeyVO(key="")

    def test_should_raise_exception_when_cache_key_is_blank(
        self,
    ) -> None:
        """Test that an exception is raised when cache key is blank."""
        with pytest.raises(InvalidCacheKeyException):
            RefreshTokenCacheKeyVO(key="   ")

    def test_should_raise_exception_when_cache_key_has_invalid_format(
        self,
    ) -> None:
        """Test that an exception is raised when cache key format is invalid."""
        with pytest.raises(InvalidCacheKeyException):
            RefreshTokenCacheKeyVO(key="invalid-key-format")

    def test_should_raise_exception_when_cache_key_is_too_long(
        self,
    ) -> None:
        """Test that an exception is raised when cache key exceeds max length."""
        invalid_key = f"cache:refresh_token:{'a' * 300}"

        with pytest.raises(InvalidCacheKeyException):
            RefreshTokenCacheKeyVO(key=invalid_key)

    def test_should_create_cache_key_when_valid_manual_key_is_provided(
        self,
    ) -> None:
        """Test that a valid manual cache key is accepted."""
        key = "cache:refresh_token:valid_key"

        refresh_token_cache_key_vo = RefreshTokenCacheKeyVO(key=key)

        assert refresh_token_cache_key_vo.key == key
