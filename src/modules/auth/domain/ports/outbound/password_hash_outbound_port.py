"""This module contains the PasswordHashOutboundPort interface."""

from abc import ABC, abstractmethod

from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class PasswordHashOutboundPort(ABC):
    """Interface for the password hashing service."""

    @abstractmethod
    def hash(self, plain_password: PlainPasswordVO) -> PasswordHashVO:
        """Hash a plain password and return the hashed version.

        Args:
            plain_password (PlainPasswordVO): The plain password to be hashed.

        Returns:
            PasswordHashVO: The hashed password.
        """
        pass
