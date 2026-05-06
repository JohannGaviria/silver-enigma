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


class InvalidTokenException(BaseDomainException):
    """Exception raised when a token is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidTokenException."""
        self.errors = error
        super().__init__("Invalid token.")
