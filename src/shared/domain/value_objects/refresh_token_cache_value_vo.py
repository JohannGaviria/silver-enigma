"""This module contains the RefreshTokenCacheValueVO class."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from src.shared.domain.exceptions.exception import InvalidRefreshTokenInputException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class RefreshTokenCacheValueVO(BaseValueObject):
    """Value Object representing the input data required to generate a refresh token.

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
            InvalidRefreshTokenInputException: If any of the attributes are invalid.
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
            raise InvalidRefreshTokenInputException(errors)

    @classmethod
    def create(cls, sub: UUID) -> "RefreshTokenCacheValueVO":
        """Factory method to create a RefreshTokenCacheValueVO with an auto-generated jti.

        Args:
            sub (UUID): The subject identifier (user ID) to associate with the refresh token.
        """
        return cls(jti=uuid4(), sub=sub)
