"""This module contains the UserRepositoryPort interface."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum


class UserRepositoryPort(ABC):
    """Interface for the User Repository, defining the contract for user-related data operations."""

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
