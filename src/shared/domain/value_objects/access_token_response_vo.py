"""This module contains the AccessTokenResponseVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.token_exception import (
    InvalidAccessTokenResponseException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject
from src.shared.domain.value_objects.token_vo import TokenVO


@dataclass(frozen=True)
class AccessTokenResponseVO(BaseValueObject):
    """Value Object representing the response data returned after generating an access token.

    Attributes:
        access_token (TokenVO): The signed JWT access token.
        token_type (str): The token scheme. Always ``"Bearer"``.
        expires_in (int): Seconds until the access token expires (600 = 10 min).
    """

    access_token: TokenVO
    token_type: str
    expires_in: int

    def _validate(self) -> None:
        """Validate the attributes of the AccessTokenResponseVO.

        Raises:
            InvalidAccessTokenResponseException: If any of the attributes are invalid.
        """
        errors: list = []

        if self.access_token is None:
            errors.append("access_token cannot be empty.")
        if not isinstance(self.access_token, TokenVO):
            errors.append("access_token must be a valid TokenVO instance.")
        if self.token_type is None or not self.token_type.strip():
            errors.append("token_type cannot be empty.")
        if self.token_type not in ["Bearer"]:
            errors.append(f"Invalid token_type: {self.token_type}")
        if self.expires_in <= 0:
            errors.append("expires_in must be positive.")

        if errors:
            raise InvalidAccessTokenResponseException(errors)
