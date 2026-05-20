import pytest

from src.shared.domain.exceptions.exception import InvalidRefreshTokenResponseException
from src.shared.domain.value_objects.refresh_token_response_vo import (
    RefreshTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class TestRefreshTokenResponseVO:
    def test_should_create_refresh_token_response_when_valid_data_is_provided(
        self, token: str
    ) -> None:
        """Test that the RefreshTokenResponseVO is created successfully.

        when valid data is provided.
        """
        refresh_token_vo = RefreshTokenResponseVO(
            refresh_token=TokenVO(token=token),
            expires_in=259200,
        )

        assert refresh_token_vo.refresh_token == TokenVO(token=token)
        assert refresh_token_vo.expires_in == 259200

    def test_should_raise_exception_when_refresh_token_is_none(self) -> None:
        """Test that the RefreshTokenResponseVO raises an InvalidRefreshTokenResponseException.

        when the refresh token is None.
        """
        with pytest.raises(InvalidRefreshTokenResponseException):
            RefreshTokenResponseVO(
                refresh_token=None,  # type: ignore
                expires_in=259200,
            )

    @pytest.mark.parametrize("refresh_token", ["", " ", 123])
    def test_should_raise_exception_when_refresh_token_is_not_a_token_vo(
        self, refresh_token: str | int
    ) -> None:
        """Test that the RefreshTokenResponseVO raises an InvalidRefreshTokenResponseException.

        when the refresh token is not a valid TokenVO instance.
        """
        with pytest.raises(InvalidRefreshTokenResponseException):
            RefreshTokenResponseVO(
                refresh_token=refresh_token,  # type: ignore
                expires_in=259200,
            )

    @pytest.mark.parametrize("expires_in", [0, -259200])
    def test_should_raise_exception_when_expires_in_is_invalid(
        self, token: str, expires_in: int
    ) -> None:
        """Test that the RefreshTokenResponseVO raises an InvalidRefreshTokenResponseException.

        when the expires_in value is invalid.
        """
        with pytest.raises(InvalidRefreshTokenResponseException):
            RefreshTokenResponseVO(
                refresh_token=TokenVO(token=token),
                expires_in=expires_in,
            )
