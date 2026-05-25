"""This module contains the session exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidRefreshTokenCacheValueException(BaseDomainException):
    """Exception raised when the refresh token cache value is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidRefreshTokenCacheValueException.

        Args:
            errors (list[str]): A list of error messages describing
                the validation failures for the refresh token cache value.
        """
        self.errors = errors
        super().__init__("Invalid refresh token cache value.")


class AuthenticationFailedException(BaseDomainException):
    """Exception raised when user authentication fails due to invalid credentials."""

    def __init__(self) -> None:
        """Initializes the AuthenticationFailedException."""
        super().__init__("Authentication failed due to invalid credentials.")


class InsufficientPermissionsException(BaseDomainException):
    """Exception raised when user authentication fails due to insufficient permissions."""

    def __init__(self, error: str) -> None:
        """Initializes the InsufficientPermissionsException.

        Args:
            error (str): A message describing the validation failure for the email address.
        """
        self.error = error
        super().__init__("Insufficient permissions.")


class SessionNotFoundException(BaseDomainException):
    """Exception raised when a session is not found in the cache."""

    def __init__(self) -> None:
        """Initializes the SessionNotFoundException."""
        super().__init__("Session not found.")
