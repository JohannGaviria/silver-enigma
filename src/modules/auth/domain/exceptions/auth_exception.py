"""This module contains custom exceptions related to authentication domain logic."""

from src.shared.domain.exceptions.exception import BaseDomainException


class InvalidNameException(BaseDomainException):
    """Exception raised when a name is invalid."""

    def __init__(self, name: str, errors: list[str]) -> None:
        """Initializes the InvalidNameException.

        Args:
            name (str): The name that failed validation.
            errors (list[str]): A list of error messages describing the validation
                failures for the name.
        """
        self.name = name
        self.errors = errors
        super().__init__("Invalid name provided.")


class InvalidEmailException(BaseDomainException):
    """Exception raised when an email address is invalid."""

    def __init__(self, email: str, error: list[str]) -> None:
        """Initializes the InvalidEmailException.

        Args:
            email (str): The email address that failed validation.
            error (list[str]): A list of error messages describing the validation failures for the email address.
        """
        self.email = email
        self.errors = error
        super().__init__("Invalid email address provided.")


class InvalidPasswordHashException(BaseDomainException):
    """Exception raised when a password hash is invalid."""

    def __init__(self, error: str) -> None:
        """Initializes the InvalidPasswordHashException.

        Args:
            error (str): A message describing the validation failure for the password hash.
        """
        self.errors = error
        super().__init__("Invalid password hash.")


class InvalidPlainPasswordException(BaseDomainException):
    """Exception raised when a plain password does not meet the defined validation criteria."""

    def __init__(self, errors: list[str]) -> None:
        """Initializes the InvalidPasswordException.

        Args:
            errors (list[str]): A list of error messages describing the validation failures.
        """
        self.errors = errors
        super().__init__("Invalid plain password provided.")


class AdminAlreadyExistsException(BaseDomainException):
    """Exception raised when an attempt is made to create an admin user but one already exists."""

    def __init__(self) -> None:
        """Initializes the AdminAlreadyExistsException."""
        super().__init__("An admin user already exists.")


class UserRepositoryException(BaseDomainException):
    """Exception raised for errors that occur within the UserRepository."""

    def __init__(self, error: str) -> None:
        """Initializes the UserRepositoryException.

        Args:
            error (str): A message describing the error that occurred within the UserRepository.
        """
        self.errors = error
        super().__init__("An error occurred in the UserRepository.")


class UserAlreadyExistsException(BaseDomainException):
    """Exception raised when an attempt is made to create a user but one with the same email already exists."""

    def __init__(self, error: str) -> None:
        """Initializes the UserAlreadyExistsException.

        Args:
            error (str): A message describing the validation failure for the email address.
        """
        self.errors = error
        super().__init__("A user with the same email already exists.")


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
