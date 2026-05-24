"""This module contains the LogoutAPIMapper class."""

from src.modules.auth.application.dtos.logout_dto import LogoutCommandDto
from src.modules.auth.presentation.api.schemas.logout_schema import LogoutRequestSchema


class LogoutAPIMapper:
    """Mapper for the LogoutRequestSchema and LogoutCommandDto."""

    @staticmethod
    def to_command(request: LogoutRequestSchema) -> LogoutCommandDto:
        """Convert LogoutRequestSchema to LogoutCommandDto.

        Args:
            request (LogoutRequestSchema): The request schema to be converted.

        Returns:
            LogoutCommandDto: The command dto.
        """
        return LogoutCommandDto(refresh_token=request.refresh_token)
