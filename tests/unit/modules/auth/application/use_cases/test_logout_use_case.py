from unittest.mock import MagicMock, Mock

import pytest

from src.modules.auth.application.dtos.logout_dto import LogoutCommandDto
from src.modules.auth.application.use_cases.logout_use_case import LogoutUseCase
from src.shared.domain.exceptions.exception import InvalidTokenException


class TestLogoutUserUseCase:
    @pytest.mark.asyncio
    async def test_should_logout_user_when_refresh_token_is_valid(
        self, logger_factory_mock: Mock, cache_outbound_mock: MagicMock, token: str
    ) -> None:
        """Test that the execute method logs out the user when the refresh token is valid."""
        cache_outbound_mock.delete.return_value = None

        use_case = LogoutUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = LogoutCommandDto(refresh_token=token)

        await use_case.execute(command=command)

    @pytest.mark.asyncio
    async def test_should_delete_refresh_token_from_cache_when_logging_out(
        self, logger_factory_mock: Mock, cache_outbound_mock: MagicMock, token: str
    ) -> None:
        """Test that the execute method deletes the refresh token from cache when logging out."""
        use_case = LogoutUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = LogoutCommandDto(refresh_token=token)

        await use_case.execute(command=command)

        cache_outbound_mock.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_refresh_token_is_invalid(
        self, cache_outbound_mock: MagicMock, logger_factory_mock: Mock
    ) -> None:
        """Test that the execute method raises an exception when the refresh token is invalid."""
        cache_outbound_mock.delete.return_value = None

        use_case = LogoutUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
        )

        command = LogoutCommandDto(refresh_token="")

        with pytest.raises(InvalidTokenException):
            await use_case.execute(command=command)

        cache_outbound_mock.delete.assert_not_awaited()
