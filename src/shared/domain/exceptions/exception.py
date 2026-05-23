"""This module contains custom exceptions for the domain layer."""


class BaseDomainException(Exception):
    """Base class for domain-specific exceptions."""

    pass


class InvalidAccessTokenPayloadException(BaseDomainException):
    """Exception raised when the access token payload is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenPayloadException."""
        self.errors = errors
        super().__init__("Invalid access token payload.")


class InvalidAccessTokenInputException(BaseDomainException):
    """Exception raised when the access token input data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenInputException."""
        self.errors = errors
        super().__init__("Invalid access token input.")


class InvalidAccessTokenResponseException(BaseDomainException):
    """Exception raised when the access token response data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenResponseException."""
        self.errors = errors
        super().__init__("Invalid access token response.")


class InvalidRefreshTokenInputException(BaseDomainException):
    """Exception raised when the refresh token input data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidRefreshTokenInputException."""
        self.errors = errors
        super().__init__("Invalid refresh token input.")


class InvalidRefreshTokenResponseException(BaseDomainException):
    """Exception raised when the refresh token response data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidRefreshTokenResponseException."""
        self.errors = errors
        super().__init__("Invalid refresh token response.")


class AuthenticationTokenMissingException(BaseDomainException):
    """Exception raised when no authentication token is provided."""

    def __init__(self) -> None:
        """Initializes the AuthenticationTokenMissingException."""
        super().__init__("Authentication credentials were not provided.")


class ExpiredTokenException(BaseDomainException):
    """Exception raised when the access token has expired."""

    def __init__(self) -> None:
        """Initializes the ExpiredTokenException."""
        super().__init__("Your session has expired. Please authenticate again.")


class InvalidTokenException(BaseDomainException):
    """Exception raised when the access token is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidTokenException."""
        self.errors = error
        super().__init__("Authentication failed due to an invalid access token.")


class InvalidCacheKeyException(BaseDomainException):
    """Exception raised when a cache key is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheKeyException."""
        self.errors = errors
        super().__init__("Invalid cache key.")


class InvalidCacheTTLException(BaseDomainException):
    """Exception raised when a cache TTL value is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheTTLException."""
        self.errors = errors
        super().__init__("Invalid cache TTL.")


class InvalidCacheEntryException(BaseDomainException):
    """Exception raised when a cache entry is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidCacheEntryException."""
        self.errors = errors
        super().__init__("Invalid cache entry.")


class CacheRetrievalException(BaseDomainException):
    """Exception raised when there is an error retrieving data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheRetrievalException."""
        self.errors = error
        super().__init__("Error retrieving data from cache.")


class CacheStorageException(BaseDomainException):
    """Exception raised when there is an error storing data in the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheStorageException."""
        self.errors = error
        super().__init__("Error storing data in cache.")


class CacheDeletionException(BaseDomainException):
    """Exception raised when there is an error deleting data from the cache."""

    def __init__(self, error: str) -> None:
        """Initializes the CacheDeletionException."""
        self.errors = error
        super().__init__("Error deleting data from cache.")
