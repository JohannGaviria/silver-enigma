"""This module contains the LogoutRequestSchema class."""

from pydantic import BaseModel


class LogoutRequestSchema(BaseModel):
    """Schema for the logout request.

    Attributes:
        refresh_token (str): The refresh token of the user to be logged out.
    """

    refresh_token: str
