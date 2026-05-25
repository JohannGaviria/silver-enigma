"""This module contains the user exceptions."""

from src.shared.domain.exceptions.base_exception import BaseDomainException


class UserNotFoundException(BaseDomainException):
    """Exception raised when a user is not found in the database."""

    def __init__(self) -> None:
        """Initializes the UserNotFoundException."""
        super().__init__("User not found.")


class UserAlreadyExistsException(BaseDomainException):
    """Exception raised when an attempt is made to create a user but one with the same email already exists."""

    def __init__(self, error: str) -> None:
        """Initializes the UserAlreadyExistsException.

        Args:
            error (str): A message describing the validation failure for the email address.
        """
        self.error = error
        super().__init__("A user with the same email already exists.")


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
        self.error = error
        super().__init__("An error occurred in the UserRepository.")
