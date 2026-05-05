import pytest

from src.shared.domain.exceptions.exception import InvalidAccessTokenException
from src.shared.domain.value_objects.access_token_vo import AccessTokenVO


class TestAccessTokenVO:
    def test_should_create_access_token_when_valid_data_is_provided(
        self, token: str, access_token_type: list[str]
    ) -> None:
        """Test that the AccessTokenVO is created successfully.

        when valid data is provided.
        """
        access_token_vo = AccessTokenVO(
            access_token=token, token_type=access_token_type[0], expires_in=600
        )

        assert access_token_vo.access_token == token
        assert access_token_vo.token_type == access_token_type[0]
        assert access_token_vo.expires_in == 600

    @pytest.mark.parametrize("access_token", ["", " ", None])
    def test_should_raise_exception_when_access_token_is_invalid(
        self, access_token: str | None, access_token_type: list[str]
    ) -> None:
        """Test that the AccessTokenVO raises an InvalidAccessTokenException.

        when the access token is invalid.
        """
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(
                access_token=access_token,  # type: ignore
                token_type=access_token_type[0],
                expires_in=600,
            )

    @pytest.mark.parametrize("access_token_type", ["", " ", "invalid-token-type", None])
    def test_should_raise_exception_when_access_token_type_is_invalid(
        self, token: str, access_token_type: str | None
    ) -> None:
        """Test that the AccessTokenVO raises an InvalidAccessTokenException.

        when the access token type is invalid.
        """
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(
                access_token=token,
                token_type=access_token_type,  # type: ignore
                expires_in=600,
            )

    @pytest.mark.parametrize("expires_in", [0, -600])
    def test_should_raise_exception_when_expires_in_is_invalid(
        self, token: str, access_token_type: list[str], expires_in: int
    ) -> None:
        """Test that the AccessTokenVO raises an InvalidAccessTokenException.

        when the expires_in value is invalid.
        """
        with pytest.raises(InvalidAccessTokenException):
            AccessTokenVO(
                access_token=token,
                token_type=access_token_type[0],
                expires_in=expires_in,
            )
