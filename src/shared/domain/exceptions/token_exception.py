"""This module contains the token exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class InvalidAccessTokenPayloadException(BaseDomainException):
    """Exception raised when the access token payload is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenPayloadException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid access token payload.")


class InvalidAccessTokenInputException(BaseDomainException):
    """Exception raised when the access token input data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenInputException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid access token input.")


class InvalidAccessTokenResponseException(BaseDomainException):
    """Exception raised when the access token response data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidAccessTokenResponseException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid access token response.")


class InvalidRefreshTokenInputException(BaseDomainException):
    """Exception raised when the refresh token input data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidRefreshTokenInputException.

        Args:
            errors (list[str]): A list of error messages.
        """
        self.errors = errors
        super().__init__("Invalid refresh token input.")


class InvalidRefreshTokenResponseException(BaseDomainException):
    """Exception raised when the refresh token response data is invalid."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidRefreshTokenResponseException.

        Args:
            errors (list[str]): A list of error messages.
        """
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
        """Initializes the InvalidTokenException.

        Args:
            error (str): A list of error messages.
        """
        self.errors = error
        super().__init__("Authentication failed due to an invalid access token.")
