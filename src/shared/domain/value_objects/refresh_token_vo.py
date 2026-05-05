"""This module contains the RefreshTokenVO class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.shared.domain.exceptions.exception import InvalidRefreshTokenException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class RefreshTokenVO(BaseValueObject):
    """Value Object representing a refresh token.

    Attributes:
        refresh_token (str): The refresh token string.
        jti (UUID): Unique identifier for the token.
        user_id (UUID): The ID of the user associated with the token.
        expires_at (datetime): Expiration time of the refresh token.
    """

    refresh_token: str
    jti: UUID
    user_id: UUID
    expires_at: datetime

    def _validate(self) -> None:
        """Validate the attributes of the RefreshTokenVO.

        Raises:
            InvalidRefreshTokenException: If any of the attributes are invalid.
        """
        errors: list = []

        if self.refresh_token is None or not self.refresh_token.strip():
            errors.append("refresh_token cannot be empty.")
        if self.jti is None:
            errors.append("jti cannot be empty.")
        if not isinstance(self.jti, UUID):
            errors.append("jti must be a valid UUID.")
        if self.user_id is None:
            errors.append("user_id cannot be empty.")
        if not isinstance(self.user_id, UUID):
            errors.append("user_id must be a valid UUID.")
        if self.expires_at <= datetime.now(UTC):
            errors.append("expires_at must be in the future.")

        if errors:
            raise InvalidRefreshTokenException(errors)
