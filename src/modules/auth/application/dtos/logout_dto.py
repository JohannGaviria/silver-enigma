"""This module contains the LogoutDto class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutCommandDto:
    """Command DTO for the LogoutUseCase.

    Attributes:
        refresh_token (str): The refresh token of the user to be logged out.
    """

    refresh_token: str
