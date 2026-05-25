"""This module contains the cache exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidCacheKeyException(BaseDomainException):
    """Exception raised when a cache key is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheKeyException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid cache key.")


class InvalidCacheTTLException(BaseDomainException):
    """Exception raised when a cache TTL value is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheTTLException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid cache TTL.")


class InvalidCacheEntryException(BaseDomainException):
    """Exception raised when a cache entry is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheEntryException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid cache entry.")


class CacheRetrievalException(BaseDomainException):
    """Exception raised when there is an error retrieving data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheRetrievalException.

        Args:
            error (str): A list of error messages.
        """
        self.errors = error
        super().__init__("Error retrieving data from cache.")


class CacheStorageException(BaseDomainException):
    """Exception raised when there is an error storing data in the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheStorageException.

        Args:
            error (str): A list of error messages.
        """
        self.errors = error
        super().__init__("Error storing data in cache.")


class CacheDeletionException(BaseDomainException):
    """Exception raised when there is an error deleting data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheDeletionException.

        Args:
            error (str): A list of error messages.
        """
        self.errors = error
        super().__init__("Error deleting data from cache.")
