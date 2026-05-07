"""This module contains the CacheValueVO class."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Self

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CacheValueVO(BaseValueObject):
    """Value object for cache value."""

    def _validate(self) -> None:
        """Validation logic for cache value."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert the cache value to a dictionary.

        Returns:
            dict[str, Any]: The cache value as a dictionary.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a cache value from a dictionary.

        Args:
            data (dict[str, Any]): The dictionary to create the cache value from.

        Returns:
            Self: The created cache value.
        """
        pass
