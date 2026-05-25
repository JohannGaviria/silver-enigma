from uuid import UUID

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.session_exception import (
    InvalidRefreshTokenCacheValueException,
)
from src.modules.auth.domain.value_objects.refresh_token_cache_value_vo import (
    RefreshTokenCacheValueVO,
)


class TestRefreshTokenCacheValueVO:
    def test_should_create_refresh_token_cache_value_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the RefreshTokenCacheValueVO is created successfully when valid data is provided."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())
        expires_in = faker.random_int(min=1, max=1000)

        refresh_token_cache_value_vo = RefreshTokenCacheValueVO(
            jti=jti, sub=sub, expires_in=expires_in
        )

        assert refresh_token_cache_value_vo.jti == jti
        assert refresh_token_cache_value_vo.sub == sub
        assert refresh_token_cache_value_vo.expires_in == expires_in

    def test_should_create_refresh_token_cache_value_via_factory_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that RefreshTokenCacheValueVO.create() generates a valid VO with an auto-generated jti."""
        sub = UUID(faker.uuid4())
        expires_in = faker.random_int(min=1, max=1000)

        refresh_token_cache_value_vo = RefreshTokenCacheValueVO.create(
            sub=sub, expires_in=expires_in
        )

        assert isinstance(refresh_token_cache_value_vo.jti, UUID)
        assert refresh_token_cache_value_vo.sub == sub

    def test_should_generate_unique_jti_on_each_factory_call(
        self, faker: Faker
    ) -> None:
        """Test that RefreshTokenCacheValueVO.create() generates a different jti on each call."""
        sub = UUID(faker.uuid4())
        expires_in = faker.random_int(min=1, max=1000)

        first = RefreshTokenCacheValueVO.create(sub=sub, expires_in=expires_in)
        second = RefreshTokenCacheValueVO.create(sub=sub, expires_in=expires_in)

        assert first.jti != second.jti

    def test_should_raise_exception_when_jti_is_none(self, faker: Faker) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the jti is None.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=None,  # type: ignore
                sub=UUID(faker.uuid4()),
                expires_in=faker.random_int(min=1, max=1000),
            )

    @pytest.mark.parametrize("jti", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_jti_is_not_a_uuid(
        self, faker: Faker, jti: str | int
    ) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the jti is not a valid UUID.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=jti,  # type: ignore
                sub=UUID(faker.uuid4()),
                expires_in=faker.random_int(min=1, max=1000),
            )

    def test_should_raise_exception_when_sub_is_none(self, faker: Faker) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the sub is None.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=UUID(faker.uuid4()),
                sub=None,  # type: ignore
                expires_in=faker.random_int(min=1, max=1000),
            )

    @pytest.mark.parametrize("sub", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_sub_is_not_a_uuid(
        self, faker: Faker, sub: str | int
    ) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the sub is not a valid UUID.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=UUID(faker.uuid4()),
                sub=sub,  # type: ignore
                expires_in=faker.random_int(min=1, max=1000),
            )

    def test_should_raise_exception_when_expires_in_is_none(self, faker: Faker) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the expires_in is None.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                expires_in=None,  # type: ignore
            )

    @pytest.mark.parametrize("expires_in", [-999, -1, 0])
    def test_should_raise_exception_when_expires_in_is_less_than_0(
        self, faker: Faker, expires_in: int
    ) -> None:
        """Test that the RefreshTokenCacheValueVO raises an InvalidRefreshTokenCacheValueException.

        when the expires_in is less than 0.
        """
        with pytest.raises(InvalidRefreshTokenCacheValueException):
            RefreshTokenCacheValueVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                expires_in=expires_in,  # type: ignore
            )
