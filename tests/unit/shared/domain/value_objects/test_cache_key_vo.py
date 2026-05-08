# tests/unit/shared/domain/value_objects/test_cache_key_vo.py

import pytest

from src.shared.domain.exceptions.exception import InvalidCacheKeyException
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO


class TestCacheKeyVO:
    def test_should_create_cache_key_when_valid_key_is_provided(
        self,
    ) -> None:
        """Test that a valid cache key is created successfully."""
        key = "cache:user:123"

        cache_key_vo = CacheKeyVO(key=key)

        assert cache_key_vo.key == key

    @pytest.mark.parametrize(
        "key",
        [
            "cache:user:123",
            "cache:session:abc",
            "cache:session:abc:def",
            "cache:refresh_token:abc123",
            "cache:user_profile:user_1",
        ],
    )
    def test_should_accept_valid_cache_key_formats(
        self,
        key: str,
    ) -> None:
        """Test that valid cache key formats are accepted."""
        cache_key_vo = CacheKeyVO(key=key)

        assert cache_key_vo.key == key

    def test_should_raise_exception_when_key_is_none(
        self,
    ) -> None:
        """Test that an exception is raised when key is None."""
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=None)  # type: ignore

    @pytest.mark.parametrize(
        "key",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_raise_exception_when_key_is_empty_or_blank(
        self,
        key: str,
    ) -> None:
        """Test that an exception is raised when key is empty or blank."""
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=key)

    @pytest.mark.parametrize(
        "key",
        [
            "invalid",
            "cache",
            "cache:",
            "cache:user",
            "cache::123",
            "user:123",
            "cache:user:",
            "cache:user:123:",
            "cache:user:123::extra",
        ],
    )
    def test_should_raise_exception_when_key_format_is_invalid(
        self,
        key: str,
    ) -> None:
        """Test that an exception is raised when key format is invalid."""
        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=key)

    def test_should_raise_exception_when_key_exceeds_max_length(
        self,
    ) -> None:
        """Test that an exception is raised when key exceeds max length."""
        key = f"cache:user:{'a' * 300}"

        with pytest.raises(InvalidCacheKeyException):
            CacheKeyVO(key=key)

    def test_str_method_should_return_key_string(self) -> None:
        """Test that the __str__ method of CacheKeyVO returns the token string."""
        cache_key_vo = CacheKeyVO("cache:user:123")
        assert str(cache_key_vo) == "cache:user:123"
