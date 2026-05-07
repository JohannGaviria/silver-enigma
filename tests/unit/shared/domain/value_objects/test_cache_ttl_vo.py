# tests/unit/shared/domain/value_objects/test_cache_ttl_vo.py

import pytest

from src.shared.domain.exceptions.exception import InvalidCacheTTLException
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO


class TestCacheTTLVO:
    def test_should_create_cache_ttl_when_valid_seconds_are_provided(
        self,
    ) -> None:
        """Test that CacheTTLVO is created successfully with valid seconds."""
        ttl = CacheTTLVO(seconds=3600)

        assert ttl.seconds == 3600

    @pytest.mark.parametrize(
        "seconds",
        [
            0,
            1,
            60,
            3600,
            259200,
        ],
    )
    def test_should_accept_valid_ttl_values(
        self,
        seconds: int,
    ) -> None:
        """Test that valid TTL values are accepted."""
        ttl = CacheTTLVO(seconds=seconds)

        assert ttl.seconds == seconds

    def test_should_raise_exception_when_seconds_is_none(
        self,
    ) -> None:
        """Test that an exception is raised when seconds is None."""
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=None)  # type: ignore

    @pytest.mark.parametrize(
        "seconds",
        [
            -1,
            -60,
            -999,
        ],
    )
    def test_should_raise_exception_when_seconds_is_negative(
        self,
        seconds: int,
    ) -> None:
        """Test that an exception is raised when seconds is negative."""
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=seconds)

    @pytest.mark.parametrize(
        "seconds",
        [
            259201,
            300000,
            999999,
        ],
    )
    def test_should_raise_exception_when_seconds_exceed_max_limit(
        self,
        seconds: int,
    ) -> None:
        """Test that an exception is raised when seconds exceed max limit."""
        with pytest.raises(InvalidCacheTTLException):
            CacheTTLVO(seconds=seconds)
