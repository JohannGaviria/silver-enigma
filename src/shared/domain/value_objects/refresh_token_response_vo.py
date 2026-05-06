"""This module contains the RefreshTokenResponseVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.exception import InvalidRefreshTokenResponseException
from src.shared.domain.value_objects.base_value_object import BaseValueObject
from src.shared.domain.value_objects.token_vo import TokenVO


@dataclass(frozen=True)
class RefreshTokenResponseVO(BaseValueObject):
    """Value Object representing the response data returned after generating a refresh token.

    Attributes:
        refresh_token (TokenVO): The opaque refresh token string.
        expires_in (int): Seconds until the refresh token expires (259200 = 3 days).
    """

    refresh_token: TokenVO
    expires_in: int

    def _validate(self) -> None:
        """Validate the attributes of the RefreshTokenResponseVO.

        Raises:
            InvalidRefreshTokenResponseException: If any of the attributes are invalid.
        """
        errors: list = []

        if self.refresh_token is None:
            errors.append("refresh_token cannot be empty.")
        if not isinstance(self.refresh_token, TokenVO):
            errors.append("refresh_token must be a valid TokenVO instance.")
        if self.expires_in <= 0:
            errors.append("expires_in must be positive.")

        if errors:
            raise InvalidRefreshTokenResponseException(errors)
