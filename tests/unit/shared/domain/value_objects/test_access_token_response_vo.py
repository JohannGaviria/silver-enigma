import pytest
from faker import Faker

from src.shared.domain.exceptions.exception import InvalidAccessTokenResponseException
from src.shared.domain.value_objects.access_token_response_vo import (
    AccessTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class TestAccessTokenResponseVO:
    def test_should_create_access_token_response_when_valid_data_is_provided(
        self, faker: Faker, token: str, access_token_type: list[str]
    ) -> None:
        """Test that the AccessTokenResponseVO is created successfully when valid data is provided."""
        access_token_vo = AccessTokenResponseVO(
            access_token=TokenVO(token=token),
            token_type=access_token_type[0],
            expires_in=600,
        )

        assert access_token_vo.access_token == TokenVO(token=token)
        assert access_token_vo.token_type == access_token_type[0]
        assert access_token_vo.expires_in == 600

    def test_should_raise_exception_when_access_token_is_none(
        self, access_token_type: list[str]
    ) -> None:
        """Test that the AccessTokenResponseVO raises an InvalidAccessTokenResponseException.

        when the access token is None.
        """
        with pytest.raises(InvalidAccessTokenResponseException):
            AccessTokenResponseVO(
                access_token=None,  # type: ignore
                token_type=access_token_type[0],
                expires_in=600,
            )

    @pytest.mark.parametrize("access_token", ["", " ", 123])
    def test_should_raise_exception_when_access_token_is_not_a_token_vo(
        self, access_token: str | int, access_token_type: list[str]
    ) -> None:
        """Test that the AccessTokenResponseVO raises an InvalidAccessTokenResponseException.

        when the access token is not a valid TokenVO instance.
        """
        with pytest.raises(InvalidAccessTokenResponseException):
            AccessTokenResponseVO(
                access_token=access_token,  # type: ignore
                token_type=access_token_type[0],
                expires_in=600,
            )

    @pytest.mark.parametrize("token_type", ["", " ", "invalid-token-type", None])
    def test_should_raise_exception_when_token_type_is_invalid(
        self, token: str, token_type: str | None
    ) -> None:
        """Test that the AccessTokenResponseVO raises an InvalidAccessTokenResponseException.

        when the token type is invalid.
        """
        with pytest.raises(InvalidAccessTokenResponseException):
            AccessTokenResponseVO(
                access_token=TokenVO(token=token),
                token_type=token_type,  # type: ignore
                expires_in=600,
            )

    @pytest.mark.parametrize("expires_in", [0, -600])
    def test_should_raise_exception_when_expires_in_is_invalid(
        self, token: str, access_token_type: list[str], expires_in: int
    ) -> None:
        """Test that the AccessTokenResponseVO raises an InvalidAccessTokenResponseException.

        when the expires_in value is invalid.
        """
        with pytest.raises(InvalidAccessTokenResponseException):
            AccessTokenResponseVO(
                access_token=TokenVO(token=token),
                token_type=access_token_type[0],
                expires_in=expires_in,
            )
