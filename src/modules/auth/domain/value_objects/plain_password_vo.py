"""This module contains the PlainPasswordVO class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.auth_exception import InvalidPasswordException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class PlainPasswordVO(BaseValueObject):
    """Value object representing a plain password.

    This value object encapsulates the plain password and provides
    validation logic to ensure that the password meets defined security criteria.
    It is designed to be used temporarily during user registration or password
    change processes, and should not be stored or exposed in any persistent form.

    Attributes:
        plain_password (str): The plain password string to be validated.
    """

    plain_password: str

    def _validate(self) -> None:
        r"""Validates the plain password against defined security criteria.

        The validation checks include:
        - Minimum length of 8 characters.
        - At least one uppercase character.
        - At least one lowercase character.
        - At least one numeric character.
        - At least one special character from the set `!@#$%^&*()-_=+[]{}|;:,.<>?/\\`

        Raises:
            InvalidPasswordException: If the plain password does not meet the validation criteria.
        """
        errors = []
        SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/\\"
        if self.plain_password is None:
            raise InvalidPasswordException("Password cannot be None.")
        if len(self.plain_password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in self.plain_password):
            errors.append("Password must contain at least one uppercase character.")
        if not any(c.islower() for c in self.plain_password):
            errors.append("Password must contain at least one lowercase character.")
        if not any(c.isdigit() for c in self.plain_password):
            errors.append("Password must contain at least one numeric character.")
        if not any(c in SPECIAL_CHARS for c in self.plain_password):
            errors.append("Password must contain at least one special character.")

        if errors:
            raise InvalidPasswordException(errors)

    def __str__(self) -> str:
        """Returns the plain password as a string.

        Note: This method should be used with caution, as it exposes the plain password.

        Returns:
            str: The plain password.
        """
        return self.plain_password
