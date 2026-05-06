import pytest

from src.shared.domain.exceptions.exception import InvalidTokenException
from src.shared.domain.value_objects.token_vo import TokenVO


class TestTokenVO:
    def test_should_create_token_when_valid_value_is_provided(self, token: str) -> None:
        """Test that the TokenVO is created successfully when a valid token is provided."""
        token_vo = TokenVO(token=token)

        assert token_vo.token == token

    @pytest.mark.parametrize("token", ["", " ", None])
    def test_should_raise_exception_when_token_is_invalid(
        self, token: str | None
    ) -> None:
        """Test that the TokenVO raises an InvalidTokenException.

        when the token is empty, blank or None.
        """
        with pytest.raises(InvalidTokenException):
            TokenVO(token=token)  # type: ignore
