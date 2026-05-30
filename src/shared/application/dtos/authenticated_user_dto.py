"""This module contains the AuthenticatedUserCommandDto class."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True)
class AuthenticatedUserCommandDto:
    """Data Transfer Object for authenticated user command.

    Attributes:
        user_id (UUID): The user's ID.
        role (UserRoleEnum): The user's role.
    """

    user_id: UUID
    role: UserRoleEnum
