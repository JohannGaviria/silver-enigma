"""This module contains the PasswordHashVO class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.auth_exception import (
    InvalidPasswordHashException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class PasswordHashVO(BaseValueObject):
    """Value object representing a password hash."""

    password_hash: str

    def _validate(self) -> None:
        """Validates the password hash to ensure it is not None.

        Raises:
            InvalidPasswordHashException: If the password hash is None.
        """
        if self.password_hash is None:
            raise InvalidPasswordHashException("Password hash cannot be None.")

    def __str__(self) -> str:
        """Returns the password hash as a string.

        Returns:
            str: The password hash.
        """
        return self.password_hash
