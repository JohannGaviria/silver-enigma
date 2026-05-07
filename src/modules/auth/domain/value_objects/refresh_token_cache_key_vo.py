"""This module contains the RefreshTokenCacheKeyVO."""

import hashlib
from dataclasses import dataclass

from src.shared.domain.value_objects.cache_key_vo import CacheKeyVO
from src.shared.domain.value_objects.token_vo import TokenVO


@dataclass(frozen=True)
class RefreshTokenCacheKeyVO(CacheKeyVO):
    """Value object representing the cache key for a refresh token."""

    @classmethod
    def from_token(cls, token: TokenVO) -> "RefreshTokenCacheKeyVO":
        """Create a cache key for the refresh token using its hash.

        This ensures that the cache key is unique for each token
        and does not expose the token value itself.

        Args:
            token (TokenVO): The token for which to create the cache key.

        Returns:
            RefreshTokenCacheKeyVO: An instance of the cache key
                value object for the refresh token
        """
        token_hash = hashlib.sha256(str(token).encode()).hexdigest()
        return cls(key=f"cache:refresh_token:{token_hash}")
