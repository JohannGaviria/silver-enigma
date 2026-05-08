"""This module contains the CacheValueVO class."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CacheValueVO(BaseValueObject):
    """Value object for cache value."""

    def _validate(self) -> None:
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            dict[str, Any]: Dictionary representation of the cache value.
        """
        pass
