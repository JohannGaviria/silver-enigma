"""This module contains the NameVO class."""

from dataclasses import dataclass

from src.modules.auth.domain.exceptions.auth_exception import InvalidNameException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class NameVO(BaseValueObject):
    """Value object representing a user's name.

    This value object encapsulates the user's name and provides validation logic
    to ensure that the name is not empty and does not exceed 255 characters in length.
    It is designed to be used as a part of the UserEntity to represent the user's name
    in a structured and validated manner.

    Attributes:
        name (str): The user's name to be validated and encapsulated.
    """

    name: str

    def _validate(self) -> None:
        """Validates that the name meets the defined criteria for a valid name.

        The validation checks include:
        - Name cannot be empty or consist solely of whitespace.
        - Name cannot exceed 255 characters in length.
        - Name must include at least a first name and a last name (at least two words).
        - Name cannot have more than 4 words.

        Raises:
            InvalidNameException: If the name does not meet the validation criteria.
        """
        errors = []
        if self.name is None or not self.name.strip():
            errors.append("Name cannot be empty.")
        if len(self.name) > 255:
            errors.append("Name cannot exceed 255 characters.")

        parts = self.name.split()
        if len(parts) < 2:
            errors.append("Name must include at least first name and last name")
        if len(parts) > 4:
            errors.append("Name cannot have more than 4 words")

        if errors:
            raise InvalidNameException(self.name, errors)

    def __str__(self) -> str:
        """Returns the name as a string.

        Returns:
            str: The name.
        """
        return self.name
