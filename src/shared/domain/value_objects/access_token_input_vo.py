"""This module contains the AccessTokenInputVO class."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import InvalidAccessTokenInputException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class AccessTokenInputVO(BaseValueObject):
    """Value Object representing the input data required to generate an access token.

    The use case only provides what it already owns: the subject identity and
    its role. The adapter is responsible for generating jti and exp internally.

    Attributes:
        jti (UUID): The unique identifier for the token (JWT ID).
        sub (UUID): The subject identifier (user ID).
        role (UserRoleEnum): The role to embed in the token claims.
    """

    jti: UUID
    sub: UUID
    role: UserRoleEnum

    def _validate(self) -> None:
        """Validate the attributes of the AccessTokenInputVO.

        Raises:
            InvalidAccessTokenInputException: If any of the attributes are invalid.
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
        if not isinstance(self.role, UserRoleEnum):
            errors.append("role must be a valid UserRoleEnum.")

        if errors:
            raise InvalidAccessTokenInputException(errors)

    @classmethod
    def create(cls, sub: UUID, role: UserRoleEnum) -> "AccessTokenInputVO":
        """Factory method to create an AccessTokenInputVO with an auto-generated jti.

        Args:
            sub (UUID): The subject identifier (user ID) to associate with the access token.
            role (UserRoleEnum): The role to embed in the token claims.
        """
        return cls(jti=uuid4(), sub=sub, role=role)
