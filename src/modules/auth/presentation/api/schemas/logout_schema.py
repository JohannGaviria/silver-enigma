"""This module contains the LogoutRequestSchema class."""

from pydantic import BaseModel


class LogoutRequestSchema(BaseModel):
    """Schema for the logout request.

    Attributes:
        refresh_token (str): The refresh token of the user to be logged out.
    """

    refresh_token: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "EZQv-uaV8XEGEbrbh_RwEWUrsg8yQsI423fBulcwBDhuy5tVQpXZGhqrceMYJRdHEJclmE-KaLR5qDDbH5ZTeA",
            }
        }
    }
