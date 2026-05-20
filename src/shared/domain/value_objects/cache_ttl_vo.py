"""This module contains the CacheTTLVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.exception import InvalidCacheTTLException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CacheTTLVO(BaseValueObject):
    """Value object for cache time to live (TTL).

    Attributes:
        seconds (int): The time to live in seconds.
    """

    seconds: int

    def _validate(self) -> None:
        """Validate the value object.

        Raises:
            InvalidCacheTTLException: If the value object is invalid.
        """
        errors: list[str] = []

        if self.seconds is None:
            raise InvalidCacheTTLException(["seconds cannot be empty."])
        if self.seconds < 0:
            errors.append("seconds must be positive.")
        if self.seconds > 2592000:
            errors.append("seconds to long (max 30 days).")

        if errors:
            raise InvalidCacheTTLException(errors)
