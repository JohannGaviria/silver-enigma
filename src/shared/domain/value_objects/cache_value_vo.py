"""This module contains the CacheValueVO class."""

from dataclasses import dataclass

from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CacheValueVO(BaseValueObject):
    """Value object for cache value."""

    pass
