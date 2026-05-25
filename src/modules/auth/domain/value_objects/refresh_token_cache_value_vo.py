"""This module contains the RefreshTokenCacheValueVO class."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from src.modules.auth.domain.exceptions.session_exception import (
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
        expires_in (int): The number of seconds until the refresh token expires.
    """

    jti: UUID
    sub: UUID
    expires_in: int

    def _validate(self) -> None:
        """Validate the attributes of the RefreshTokenCacheValueVO.

        Raises:
            InvalidRefreshTokenCacheValueException: If any of the attributes are invalid.
        """
        errors: list = []

        if self.jti is None:
            raise InvalidRefreshTokenCacheValueException(["jti cannot be empty."])
        if self.sub is None:
            raise InvalidRefreshTokenCacheValueException(["sub cannot be empty."])
        if self.expires_in is None:
            raise InvalidRefreshTokenCacheValueException(
                ["expires_in cannot be empty."]
            )

        if not isinstance(self.jti, UUID):
            errors.append("jti must be a valid UUID.")
        if not isinstance(self.sub, UUID):
            errors.append("sub must be a valid UUID.")
        if not isinstance(self.expires_in, int):
            errors.append("expires_in must be an integer.")
        if self.expires_in <= 0:
            errors.append("expires_in must be greater than 0.")

        if errors:
            raise InvalidRefreshTokenCacheValueException(errors)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            dict: dictionary representation of the cache value.
        """
        return {
            "jti": str(self.jti),
            "sub": str(self.sub),
            "expires_in": self.expires_in,
        }

    @classmethod
    def create(cls, sub: UUID, expires_in: int) -> "RefreshTokenCacheValueVO":
        """Factory method to create a RefreshTokenCacheValueVO.

        Args:
            sub (UUID): The subject identifier (user ID) to associate with the refresh token.
            expires_in (int): The number of seconds until the refresh token expires.

        Returns:
            RefreshTokenCacheValueVO: The RefreshTokenCacheValueVO instance.
        """
        return cls(jti=uuid4(), sub=sub, expires_in=expires_in)
