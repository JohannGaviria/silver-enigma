"""This module contains the UserEntity class."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.enums.user_role_enum import UserRoleEnum


@dataclass(frozen=True)
class UserEntity(BaseEntity):
    """Entity representing a user in the authentication domain.

    Attributes:
        name (NameVO): The user's name encapsulated in a NameVO value object.
        email (EmailVO): The user's email encapsulated in an EmailVO value object.
        password (PasswordHashVO): The user's password hash encapsulated
            in a PasswordHashVO value object.
        role (UserRoleEnum): The user's role defined in the UserRoleEnum.
    """

    name: NameVO
    email: EmailVO
    password: PasswordHashVO
    role: UserRoleEnum

    @classmethod
    def create(
        cls, name: NameVO, email: EmailVO, password: PasswordHashVO, role: UserRoleEnum
    ) -> "UserEntity":
        """Factory method to create a new UserEntity instance with a unique ID and timestamps.

        This method generates a new UUID for the user, sets the created_at and updated_at
        timestamps to the current time in UTC, and returns a new instance of UserEntity
        with the provided name, email, password, and role.

        Args:
            name (NameVO): The user's name encapsulated in a NameVO value object.
            email (EmailVO): The user's email encapsulated in an EmailVO value object.
            password (PasswordHashVO): The user's password hash encapsulated
                in a PasswordHashVO value object.
            role (UserRoleEnum): The user's role defined in the UserRoleEnum.
        """
        datetime_now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            name=name,
            email=email,
            password=password,
            role=role,
            created_at=datetime_now,
            updated_at=datetime_now,
        )
