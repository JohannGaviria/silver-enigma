"""This module contains the TokenPayloadVO class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import InvalidTokenPayloadException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class TokenPayloadVO(BaseValueObject):
    """Value Object representing the payload of a JWT token.

    Attributes:
        jti (UUID): Unique identifier for the token.
        sub (UUID): Subject of the token, typically the user ID.
        role (UserRoleEnum): Role of the user (e.g., ADMIN, USER).
        exp (datetime): Expiration time of the token.
    """

    jti: UUID
    sub: UUID
    role: UserRoleEnum
    exp: datetime

    def _validate(self) -> None:
        """Validate the attributes of the TokenPayloadVO.

        Raises:
            InvalidTokenPayloadException: If any of the attributes are invalid.
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
        if self.role is None:
            errors.append("role cannot be empty.")
        if self.exp <= datetime.now(UTC):
            errors.append("exp must be in the future.")

        if errors:
            raise InvalidTokenPayloadException(errors)
