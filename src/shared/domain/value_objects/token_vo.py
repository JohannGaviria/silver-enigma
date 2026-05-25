"""This module contains the TokenVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.token_exception import InvalidTokenException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class TokenVO(BaseValueObject):
    """Value Object representing a token string, such as an access token or refresh token.

    Attributes:
        token (str): The token string, typically a JWT for access tokens
            or an opaque string for refresh tokens.
    """

    token: str

    def _validate(self) -> None:
        """Validate the attributes of the TokenVO.

        Raises:
            InvalidTokenException: If any of the attributes are invalid.
        """
        if self.token is None or not self.token.strip():
            raise InvalidTokenException("Token cannot be empty.")

    def __str__(self) -> str:
        """Return the string representation of the token.

        Returns:
            str: The token string.
        """
        return self.token
