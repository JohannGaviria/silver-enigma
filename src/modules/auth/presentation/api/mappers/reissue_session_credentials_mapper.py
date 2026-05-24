"""This module contains mappers for the ReissueSessionCredentials class."""

from src.modules.auth.application.dtos.reissue_session_credentials_dto import (
    ReissueSessionCredentialsCommandDto,
    ReissueSessionCredentialsResponseDto,
)
from src.modules.auth.presentation.api.schemas.reissue_session_credentials_schema import (
    AccessTokenSchema,
    RefreshTokenSchema,
    ReissueSessionCredentialsRequestSchema,
    ReissueSessionCredentialsResponseSchema,
)


class ReissueSessionCredentialsMapper:
    """Mapper for the ReissueSessionCredentialsRequestSchema and ReissueSessionCredentialsResponseSchema."""

    @staticmethod
    def to_command(
        request: ReissueSessionCredentialsRequestSchema,
    ) -> ReissueSessionCredentialsCommandDto:
        """Convert a ReissueSessionCredentialsRequestSchema to a ReissueSessionCredentialsCommandDto.

        Args:
            request (ReissueSessionCredentialsRequestSchema):
                The ReissueSessionCredentialsRequestSchema instance.

        Returns:
            ReissueSessionCredentialsCommandDto: The ReissueSessionCredentialsCommandDto instance.
        """
        return ReissueSessionCredentialsCommandDto(refresh_token=request.refresh_token)

    @staticmethod
    def to_response(
        command: ReissueSessionCredentialsResponseDto,
    ) -> ReissueSessionCredentialsResponseSchema:
        """Convert a ReissueSessionCredentialsResponseDto to a ReissueSessionCredentialsResponseSchema.

        Args:
            command (ReissueSessionCredentialsResponseDto): The ReissueSessionCredentialsResponseDto instance.

        Returns:
            ReissueSessionCredentialsResponseSchema: The ReissueSessionCredentialsResponseSchema instance.
        """
        access = AccessTokenSchema(
            token=command.access.token,
            token_type=command.access.token_type,
            expires_in=command.access.expires_in,
        )

        refresh = RefreshTokenSchema(
            token=command.refresh.token, expires_in=command.refresh.expires_in
        )

        return ReissueSessionCredentialsResponseSchema(access=access, refresh=refresh)
