# tests/unit/shared/domain/value_objects/test_cache_entry_vo.py


import pytest

from src.shared.domain.exceptions.exception import InvalidCacheEntryException
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from tests.conftest import FakeCacheValueVO


class TestCacheEntryVO:
    def test_should_create_cache_entry_when_valid_data_is_provided(
        self,
    ) -> None:
        """Test that CacheEntryVO is created successfully with valid data."""
        key = CacheKeyVO(key="cache:user:123")
        ttl = CacheTTLVO(seconds=3600)
        value = FakeCacheValueVO(value="test")

        cache_entry_vo = CacheEntryVO(
            key=key,
            ttl=ttl,
            value=value,
        )

        assert cache_entry_vo.key == key
        assert cache_entry_vo.ttl == ttl
        assert cache_entry_vo.value == value

    def test_should_raise_exception_when_key_is_none(
        self,
    ) -> None:
        """Test that an exception is raised when key is None."""
        ttl = CacheTTLVO(seconds=3600)
        value = FakeCacheValueVO(value="test")

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key=None,  # type: ignore
                ttl=ttl,
                value=value,
            )

    def test_should_raise_exception_when_key_is_invalid_type(
        self,
    ) -> None:
        """Test that an exception is raised when key is invalid."""
        ttl = CacheTTLVO(seconds=3600)
        value = FakeCacheValueVO(value="test")

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key="invalid",  # type: ignore
                ttl=ttl,
                value=value,
            )

    def test_should_raise_exception_when_ttl_is_none(
        self,
    ) -> None:
        """Test that an exception is raised when ttl is None."""
        key = CacheKeyVO(key="cache:user:123")
        value = FakeCacheValueVO(value="test")

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key=key,
                ttl=None,  # type: ignore
                value=value,
            )

    def test_should_raise_exception_when_ttl_is_invalid_type(
        self,
    ) -> None:
        """Test that an exception is raised when ttl is invalid."""
        key = CacheKeyVO(key="cache:user:123")
        value = FakeCacheValueVO(value="test")

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key=key,
                ttl="invalid",  # type: ignore
                value=value,
            )

    def test_should_raise_exception_when_value_is_none(
        self,
    ) -> None:
        """Test that an exception is raised when value is None."""
        key = CacheKeyVO(key="cache:user:123")
        ttl = CacheTTLVO(seconds=3600)

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key=key,
                ttl=ttl,
                value=None,  # type: ignore
            )

    def test_should_raise_exception_when_value_is_invalid_type(
        self,
    ) -> None:
        """Test that an exception is raised when value is invalid."""
        key = CacheKeyVO(key="cache:user:123")
        ttl = CacheTTLVO(seconds=3600)

        with pytest.raises(InvalidCacheEntryException):
            CacheEntryVO(
                key=key,
                ttl=ttl,
                value="invalid",  # type: ignore
            )
