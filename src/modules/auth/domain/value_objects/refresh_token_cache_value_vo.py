"""This module contains the RefreshTokenCacheValueVO class."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.auth.domain.exceptions.auth_exception import (
    InvalidRefreshTokenCacheValueException,
)
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True)
class RefreshTokenCacheValueVO(CacheValueVO):
    """Value object representing the value stored in cache for a refresh token.

    Attributes:
        jti (UUID): The unique identifier for the token (JWT ID) to associate with
            the refresh token.
        sub (UUID): The subject identifier (user ID) to associate with the
            refresh token.
    """

    jti: UUID
    sub: UUID

    def _validate(self) -> None:
        """Validate the attributes of the RefreshTokenCacheValueVO.

        Raises:
            InvalidRefreshTokenCacheValueException: If any of the attributes are invalid.
        """
        errors: list = []

        if self.jti is None:
            errors.append("jti cannot be empty.")
        if not isinstance(self.jti, UUID):
            errors.append("jti must be a valid UUID.")
        if self.sub is None:
            errors.append("sub cannot be empty.")
        if not isinstance(self.sub, UUID):
            errors.append("sub must be a valid UUID.")

        if errors:
            raise InvalidRefreshTokenCacheValueException(errors)

    @classmethod
    def create(cls, sub: UUID) -> "RefreshTokenCacheValueVO":
        """Factory method to create a RefreshTokenCacheValueVO with an auto-generated jti.

        Args:
            sub (UUID): The subject identifier (user ID) to associate with the refresh token.
        """
        return cls(jti=uuid4(), sub=sub)
