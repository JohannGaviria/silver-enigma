"""This module contains the EmailVO class."""

import re
from dataclasses import dataclass

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
)
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class EmailVO(BaseValueObject):
    """Value object representing an email address.

    This value object encapsulates the email address and provides validation logic
    to ensure that the email meets defined criteria for a valid email address.
    It is designed to be used as a part of the UserEntity to represent the user's email
    in a structured and validated manner.

    Attributes:
        email (str): The email address to be validated and encapsulated.
    """

    email: str

    def _validate(self) -> None:
        """Validates the email address to ensure it meets defined criteria.

        The validation checks include:
        - Email cannot be empty or consist solely of whitespace.
        - Email cannot contain whitespace characters.
        - Email cannot contain consecutive dots.
        - Email must match a standard email format.
        - Email cannot exceed 255 characters in length.

        Raises:
            InvalidEmailException: If the email address does not meet the validation criteria.
        """
        errors = []
        # This regex pattern is a simplified version that covers most common email formats,
        # but it may not cover all edge cases defined in the RFC 5322 standard.
        EMAIL_PATTERN = (
            r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,6}$"
        )
        if self.email is None or not self.email.strip():
            errors.append("Email cannot be empty.")
        if any(w in self.email for w in (" ", "\t", "\n")):
            errors.append("Email cannot contain whitespace characters.")
        if ".." in self.email:
            errors.append("Email cannot contain consecutive dots.")
        if not re.match(EMAIL_PATTERN, self.email):
            errors.append("Email format is invalid.")
        if len(self.email) > 255:
            errors.append("Email cannot exceed 255 characters.")

        if errors:
            raise InvalidEmailException(self.email, errors)

    def domain(self) -> str:
        """Extracts and returns the domain part of the email address.

        Returns:
            str: The domain part of the email address.
        """
        return self.email.split("@")[1].lower()

    def __str__(self) -> str:
        """Returns the email as a string.

        Returns:
            str: The email address.
        """
        return self.email
