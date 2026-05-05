"""This module contains the AccessTokenVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.exception import InvalidAccessTokenException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class AccessTokenVO(BaseValueObject):
    """Value Object representing an access token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token (e.g., "Bearer").
        expires_in (int): The number of seconds until the token expires.
    """

    access_token: str
    token_type: str
    expires_in: int

    def _validate(self) -> None:
        """Validate the attributes of the AccessTokenVO.

        Raises:
            InvalidAccessTokenException: If any of the attributes are invalid.
        """
        errors: list = []
        if self.access_token is None or not self.access_token.strip():
            errors.append("access_token cannot be empty.")
        if self.token_type is None or not self.token_type.strip():
            errors.append("token_type cannot be empty.")
        if self.token_type not in ["Bearer"]:
            errors.append(f"Invalid token_type: {self.token_type}")
        if self.expires_in <= 0:
            errors.append("expires_in must be positive.")

        if errors:
            raise InvalidAccessTokenException(errors)
