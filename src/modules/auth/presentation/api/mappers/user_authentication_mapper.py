"""This module contains mappers for the UserAuthentication class."""

from src.modules.auth.application.dtos.user_authentication_dto import (
    UserAuthenticationCommand,
    UserAuthenticationResponse,
)
from src.modules.auth.presentation.api.schemas.user_authentication_schema import (
    AccessTokenSchema,
    RefreshTokenSchema,
    UserAuthenticationRequestSchema,
    UserAuthenticationResponseSchema,
)


class UserAuthenticationMapper:
    """Mapper for the UserAuthenticationRequestSchema and UserAuthenticationResponseSchema."""

    @staticmethod
    def to_command(
        request: UserAuthenticationRequestSchema,
    ) -> UserAuthenticationCommand:
        """Convert a UserAuthenticationRequestSchema to a UserAuthenticationCommand.

        Args:
            request (UserAuthenticationRequestSchema): The UserAuthenticationRequestSchema instance.

        Returns:
            UserAuthenticationCommand: The UserAuthenticationCommand instance.
        """
        return UserAuthenticationCommand(email=request.email, password=request.password)

    @staticmethod
    def to_response(
        command: UserAuthenticationResponse,
    ) -> UserAuthenticationResponseSchema:
        """Convert a UserAuthenticationResponse to a UserAuthenticationResponseSchema.

        Args:
            command (UserAuthenticationResponse): The UserAuthenticationResponse instance.

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
