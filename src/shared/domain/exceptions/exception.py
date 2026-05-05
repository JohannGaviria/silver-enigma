"""This module contains custom exceptions for the domain layer."""


class BaseDomainException(Exception):
    """Base class for domain-specific exceptions."""

    pass


class InvalidTokenPayloadException(BaseDomainException):
    """Exception raised when the token payload is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidTokenPayloadException."""
        self.errors = errors
        super().__init__("Invalid token payload.")


class InvalidAccessTokenException(BaseDomainException):
    """Exception raised when the access token is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenException."""
        self.errors = errors
        super().__init__("Invalid access token.")


class InvalidRefreshTokenException(BaseDomainException):
    """Exception raised when the refresh token is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenException."""
        self.errors = errors
        super().__init__("Invalid refresh token.")
