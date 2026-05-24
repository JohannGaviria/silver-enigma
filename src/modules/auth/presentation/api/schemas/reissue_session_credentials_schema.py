"""This module contains the reissue session credentials request schema."""

from pydantic import BaseModel


class ReissueSessionCredentialsRequestSchema(BaseModel):
    """Schema for the reissue session credentials request.

    Attributes:
        refresh_token (str): The refresh token to be reissued.
    """

    refresh_token: str


class AccessTokenSchema(BaseModel):
    """Nested schema for the access token portion of the response.

    Attributes:
        token (str): The signed JWT access token.
        token_type (str): The token scheme (e.g. "Bearer").
        expires_in (int): Seconds until the access token expires.
    """

    token: str
    token_type: str
    expires_in: int


class RefreshTokenSchema(BaseModel):
    """Nested schema for the refresh token portion of the response.

    Attributes:
        token (str): The opaque refresh token string.
        expires_in (int): Seconds until the refresh token expires.
    """

    token: str
    expires_in: int


class ReissueSessionCredentialsResponseSchema(BaseModel):
    """Schema for the successful reissue session credentials response.

    Attributes:
        access (AccessTokenSchema): Access token details.
        refresh (RefreshTokenSchema): Refresh token details.
    """

    access: AccessTokenSchema
    refresh: RefreshTokenSchema

    model_config = {
        "json_schema_extra": {
            "example": {
                "access": {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
                "refresh": {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                    "expires_in": 3600,
                },
            }
        }
    }
