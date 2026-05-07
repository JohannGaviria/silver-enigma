"""This module contains the CacheKeyVO class."""

import re
from dataclasses import dataclass

from src.shared.domain.exceptions.exception import InvalidCacheKeyException
from src.shared.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class CacheKeyVO(BaseValueObject):
    """Value Object for cache keys.

    The cache key must follow the pattern: cache:{type}:{id}[:{optional}]

    Examples of valid keys:
    - cache:user:123
    - cache:session:abc:def

    Constraints:
    - Must start with "cache:"
    - Followed by a type (alphanumeric or underscore)
    - Followed by an ID (alphanumeric or underscore)
    - Optionally followed by additional segments (e.g., :extra)
    - Maximum length of 250 characters

    Attributes:
        key (str): The cache key string.
    """

    key: str

    def _validate(self) -> None:
        """Validate the cache key against defined rules.

        Raises:
            InvalidCacheKeyException: If the cache key does not meet the validation criteria.
        """
        errors: list[str] = []

        # Regex pattern:
        # Example valid keys: cache:user:123, cache:session:abc:def
        CACHE_PATTERN = r"^cache:[a-zA-Z0-9_]+:[a-zA-Z0-9_]+(:[^:]+)?$"

        if self.key is None or not self.key.strip():
            errors.append("cache_key cannot be empty.")
        if not re.match(CACHE_PATTERN, self.key):
            errors.append("Invalid cache_key format.")
        if len(self.key) > 250:
            errors.append("cache_key too long (max 250 characters).")

        if errors:
            raise InvalidCacheKeyException(errors)
