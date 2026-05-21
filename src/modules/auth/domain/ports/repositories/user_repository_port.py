"""This module contains the UserRepositoryPort interface."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class UserRepositoryPort(ABC):
    """Interface for the User Repository, defining the contract for user-related data operations."""

    @abstractmethod
    async def find_by_email(self, email: EmailVO) -> UserEntity | None:
        """Finds a user by their email address.

        Args:
            email (EmailVO): The email to check for existence.

        Returns:
            UserEntity | None: The user entity if found, or None if no user
                with the specified email exists.
        """

    @abstractmethod
    async def exists_by_role(self, role: UserRoleEnum) -> bool:
        """Checks if a user with the specified role exists in the repository.

        Args:
            role (UserRoleEnum): The role to check for existence.

        Returns:
            bool: True if a user with the specified role exists, False otherwise.
        """
        pass

    @abstractmethod
    async def save(self, entity: UserEntity) -> UserEntity:
        """Saves a UserEntity to the repository.

        Args:
            entity (UserEntity): The user entity to be saved.

        Returns:
            UserEntity: The saved user entity.
        """
        pass
