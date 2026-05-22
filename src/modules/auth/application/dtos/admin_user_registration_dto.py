"""This module contains the DTO's for the AdminUserRegistrationUseCase."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True)
class BaseAdminUserRegistrationDto:
    """Base DTO for the AdminUserRegistrationUseCase.

    Attributes:
        name (str): The name of the user to be registered.
        email (str): The email of the user to be registered.
        role (UserRoleEnum): The role of the user to be registered.
    """

    name: str
    email: str
    role: UserRoleEnum


@dataclass(frozen=True)
class AdminUserRegistrationCommandDto(BaseAdminUserRegistrationDto):
    """DTO representing the command for admin user registration.

    Attributes:
        name (str): The name of the user to be registered.
        email (str): The email of the user to be registered.
        password (str): The plain password of the user to be registered.
        role (UserRoleEnum): The role of the user to be registered.
        actor_role (UserRoleEnum): The role of the user performing the registration.
    """

    password: str
    actor_role: UserRoleEnum


@dataclass(frozen=True)
class AdminUserRegistrationResponseDto(BaseAdminUserRegistrationDto):
    """DTO representing the response of a successful admin user registration.

    Attributes:
        id (UUID): The ID of the registered user.
        name (str): The name of the registered user.
        email (str): The email of the registered user.
        role (UserRoleEnum): The role of the registered user.
        created_at (datetime): The creation timestamp of the registered user.
        updated_at (datetime): The update timestamp of the registered user.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime
