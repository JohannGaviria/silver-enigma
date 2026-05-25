"""This module contains the ReissueSessionCredentialsUseCase class."""

from src.modules.auth.application.dtos.reissue_session_credentials_dto import (
    ReissueSessionCredentialsCommandDto,
    ReissueSessionCredentialsResponseDto,
)
from src.modules.auth.domain.exceptions.session_exception import (
    SessionNotFoundException,
)
from src.modules.auth.domain.exceptions.user_exception import UserNotFoundException
from src.modules.auth.domain.ports.repositories.user_repository_port import (
    UserRepositoryPort,
)
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
from src.shared.domain.ports.outbound.token_outbound_port import TokenOutboundPort
from src.shared.domain.value_objects.access_token_input_vo import AccessTokenInputVO
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.cache_ttl_vo import CacheTTLVO
from src.shared.domain.value_objects.token_vo import TokenVO


class ReissueSessionCredentialsUseCase:
    """Use case for reissuing session credentials in the system.

    This use case checks if a refresh token exists in cache, deletes the refresh
    token from cache, gets the user associated with the refresh token, generates
    access and refresh tokens, stores the refresh token in cache, and returns
    the reissued session credentials.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        cache_outbound: CacheOutboundPort[RefreshTokenCacheValueVO],
        token_outbound: TokenOutboundPort,
        user_repository: UserRepositoryPort,
    ) -> None:
        """Initializes the ReissueSessionCredentialsUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The factory for creating loggers.
            cache_outbound (CacheOutboundPort[RefreshTokenCacheValueVO]): The service for
                caching refresh tokens.
            token_outbound (TokenOutboundPort): The service for generating access and
                refresh tokens.
            user_repository (UserRepositoryPort): The repository for user data.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.cache_outbound = cache_outbound
        self.token_outbound = token_outbound
        self.user_repository = user_repository

    async def execute(
        self, command: ReissueSessionCredentialsCommandDto
    ) -> ReissueSessionCredentialsResponseDto:
        """Executes the use case to reissue session credentials.

        Checks whether the refresh token exists in cache, deletes the refresh
        token from cache, gets the user associated with the refresh token,
        generates access and refresh tokens, stores the refresh token in cache,
        and returns the reissued session credentials.

        Args:
            command (ReissueSessionCredentialsCommandDto): The command containing the
                refresh token for reissuing session credentials.

        Returns:
            ReissueSessionCredentialsResponseDto: The response containing
                the access and refresh tokens.

        Raises:
            SessionNotFoundException: If the refresh token is not found in cache.
            UserNotFoundException: If the user associated with the refresh token is not found.
        """
        self._logger.info("Executing reissue session credentials use case")

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        refresh_token = TokenVO(command.refresh_token)

        # Build the cache key from the refresh token
        refresh_token_key = RefreshTokenCacheKeyVO.from_token(refresh_token)

        # Get the session associated with the refresh token
        session = await self.cache_outbound.get(refresh_token_key)

        # Check if the refresh token exists in cache
        if session is None:
            self._logger.warning(
                "Refresh token not found", refresh_token=str(refresh_token)
            )
            raise SessionNotFoundException()

        # Delete the refresh token from cache
        await self.cache_outbound.delete(refresh_token_key)

        # Get the user associated with the refresh token
        user = await self.user_repository.find_by_id(session.sub)
        if user is None:
            self._logger.warning("User not found", user_id=str(session.sub))
            raise UserNotFoundException()

        # Generate access and refresh tokens
        access_token_input = AccessTokenInputVO.create(user.id, user.role)
        access_token_response = self.token_outbound.generate_access(access_token_input)
        refresh_token_response = self.token_outbound.generate_refresh()

        # Build the cache entry for the refresh token
        key = RefreshTokenCacheKeyVO.from_token(refresh_token_response.refresh_token)
        ttl = CacheTTLVO(refresh_token_response.expires_in)
        value = RefreshTokenCacheValueVO.create(
            user.id, refresh_token_response.expires_in
        )

        # Store the refresh token in cache with the associated user ID and jti
        entry = CacheEntryVO(key, ttl, value)
        await self.cache_outbound.set(entry)

        self._logger.info("Refresh token successfully issued", user_id=str(user.id))

        return ReissueSessionCredentialsResponseDto.response(
            access_token=str(access_token_response.access_token),
            access_token_type=access_token_response.token_type,
            access_expires_in=access_token_response.expires_in,
            refresh_token=str(refresh_token_response.refresh_token),
            refresh_expires_in=refresh_token_response.expires_in,
        )
