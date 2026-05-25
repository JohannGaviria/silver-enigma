"""This module contains mappers for the UserAuthentication class."""

from src.modules.auth.application.dtos.user_authentication_dto import (
    UserAuthenticationCommandDto,
    UserAuthenticationResponseDto,
)
from src.modules.auth.presentation.api.schemas.user_authentication_schema import (
    AccessTokenSchema,
    RefreshTokenSchema,
    UserAuthenticationRequestSchema,
    UserAuthenticationResponseSchema,
)


class UserAuthenticationApiMapper:
    """Mapper for the UserAuthenticationSchema to UserAuthenticationDto."""

    @staticmethod
    def to_command(
        request: UserAuthenticationRequestSchema,
    ) -> UserAuthenticationCommandDto:
        """Convert a UserAuthenticationRequestSchema to a UserAuthenticationCommandDto.

        Args:
            request (UserAuthenticationRequestSchema): The UserAuthenticationRequestSchema instance.

        Returns:
            UserAuthenticationCommandDto: The UserAuthenticationCommandDto instance.
        """
        return UserAuthenticationCommandDto(
            email=request.email, password=request.password
        )

    @staticmethod
    def to_response(
        command: UserAuthenticationResponseDto,
    ) -> UserAuthenticationResponseSchema:
        """Convert a UserAuthenticationResponseDto to a UserAuthenticationResponseSchema.

        Args:
            command (UserAuthenticationResponseDto): The UserAuthenticationResponseDto instance.

        Returns:
            UserAuthenticationResponseSchema: The UserAuthenticationResponseSchema instance.
        """
        access = AccessTokenSchema(
            token=command.access.token,
            token_type=command.access.token_type,
            expires_in=command.access.expires_in,
        )

        refresh = RefreshTokenSchema(
            token=command.refresh.token, expires_in=command.refresh.expires_in
        )

        return UserAuthenticationResponseSchema(access=access, refresh=refresh)
