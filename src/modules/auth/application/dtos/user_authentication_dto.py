"""This module contains the DTO's for the UserAuthenticationUseCase."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserAuthenticationCommandDto:
    """Base DTO for the UserAuthenticationUseCase.

    Attributes:
        email (str): The email of the user to be authenticated.
        password (str): The plain password of the user to be authenticated.
    """

    email: str
    password: str


@dataclass(frozen=True)
class AccessTokenDto:
    """DTO representing the response for an access token.

    Attributes:
        token (str): The access token string.
        token_type (str): The type of the access token (e.g., "Bearer").
        expires_in (int): The expiration time in seconds for the access token.
    """

    token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class RefreshTokenDto:
    """DTO representing the response for a refresh token.

    Attributes:
        token (str): The refresh token string.
        expires_in (int): The expiration time in seconds for the refresh token.
    """

    token: str
    expires_in: int


@dataclass(frozen=True)
class UserAuthenticationResponseDto:
    """DTO representing the response of a successful user authentication.

    Attributes:
        access (AccessTokenDto): The access token response
            containing the token,type, and expiration.
        refresh (RefreshTokenDto): The refresh token response
            containing the token and expiration.
    """

    access: AccessTokenDto
    refresh: RefreshTokenDto

    @classmethod
    def response(
        cls,
        access_token: str,
        access_token_type: str,
        access_expires_in: int,
        refresh_token: str,
        refresh_expires_in: int,
    ) -> "UserAuthenticationResponseDto":
        """Factory method to create a UserAuthenticationResponseDto from token values.

        Args:
            access_token (str): The access token string.
            access_token_type (str): The type of the access token (e.g., "Bearer").
            access_expires_in (int): The expiration time in seconds for the access token.
            refresh_token (str): The refresh token string.
            refresh_expires_in (int): The expiration time in seconds for the refresh token.

        Returns:
            UserAuthenticationResponseDto: An instance of UserAuthenticationResponseDto
                containing the access and refresh token responses.
        """
        access = AccessTokenDto(
            token=access_token,
            token_type=access_token_type,
            expires_in=access_expires_in,
        )
        refresh = RefreshTokenDto(token=refresh_token, expires_in=refresh_expires_in)
        return cls(access=access, refresh=refresh)
