"""This module contains the LogoutUseCase class."""

from src.modules.auth.application.dtos.logout_dto import LogoutCommandDto
from src.modules.auth.domain.value_objects.refresh_token_cache_key_vo import (
    RefreshTokenCacheKeyVO,
)
from src.modules.auth.domain.value_objects.refresh_token_cache_value_vo import (
    RefreshTokenCacheValueVO,
)
from src.shared.domain.ports.outbound.cache_outbound_port import CacheOutboundPort
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class LogoutUseCase:
    """Use case for logging out a user."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[RefreshTokenCacheValueVO],
    ) -> None:
        """Initialize the LogoutUseCase with required dependencies.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory outbound port.
            cache_outbound (CacheOutboundPort[RefreshTokenCacheValueVO]): The cache outbound port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.cache_outbound = cache_outbound

    async def execute(self, command: LogoutCommandDto) -> None:
        """Execute the use case so that the user is logged out.

        Args:
            command (LogoutCommandDto): The command containing the details for logging out.

        Returns:
            None
        """
        self._logger.info("Executing logout use case")

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        refresh_token = TokenVO(command.refresh_token)

        # Delete the refresh token from cache
        refresh_token_key = RefreshTokenCacheKeyVO.from_token(refresh_token)
        await self.cache_outbound.delete(refresh_token_key)

        self._logger.info("User successfully logged out")

        return None
