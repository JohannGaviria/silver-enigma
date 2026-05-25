"""This module contains the CacheEntryVO class."""

from dataclasses import dataclass

from src.shared.domain.exceptions.cache_exception import InvalidCacheEntryException
from src.shared.domain.value_objects.base_value_object import BaseValueObject
from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from src.shared.domain.value_objects.cache_value_vo import CacheValueVO


@dataclass(frozen=True)
class CacheEntryVO[CacheValueType: CacheValueVO](BaseValueObject):
    """Value object representing a cache entry, containing a key, TTL, and value.

    Attributes:
        key (CacheKeyVO): The cache key.
        ttl (CacheTTLVO): The time-to-live for the cache entry.
        value (CacheValueType): The value to be cached,
            which must be a subclass of CacheValueVO.
    """

    key: CacheKeyVO
    ttl: CacheTTLVO
    value: CacheValueType

    def _validate(self) -> None:
        """Validates the cache entry data, ensuring that the key, TTL, and value are all valid.

        Raises:
            InvalidCacheEntryException: If any of the validation checks fail,
                an exception is raised containing the list of validation errors.
        """
        errors: list[str] = []

        if self.key is None:
            raise InvalidCacheEntryException(["key cannot be empty."])
        if self.ttl is None:
            raise InvalidCacheEntryException(["ttl cannot be empty."])
        if self.value is None:
            raise InvalidCacheEntryException(["value cannot be empty."])

        if not isinstance(self.key, CacheKeyVO):
            errors.append("key must be a CacheKeyVO instance.")
        if not isinstance(self.ttl, CacheTTLVO):
            errors.append("ttl must be a CacheTTLVO instance.")
        if not isinstance(self.value, CacheValueVO):
            errors.append("value must be a CacheValueVO instance.")

        if errors:
            raise InvalidCacheEntryException(errors)
