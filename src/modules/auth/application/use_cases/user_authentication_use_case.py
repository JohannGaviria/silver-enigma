"""This module contains the UserAuthenticationUseCase class."""

from src.modules.auth.application.dtos.user_authentication_dto import (
    UserAuthenticationCommand,
    UserAuthenticationResponse,
)
from src.modules.auth.domain.exceptions.auth_exception import (
    AuthenticationFailedException,
)
from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.ports.unit_of_work.user_unit_of_work_port import (
    UserUnitOfWorkPort,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
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


class UserAuthenticationUseCase:
    """Use case for user authentication in the system.

    This use case checks if a user with the provided email exists, verifies the password,
    generates access and refresh tokens, stores the refresh token in cache,
    and returns the authentication response. All operations are performed within
    a single transaction to ensure consistency.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        unit_of_work: UserUnitOfWorkPort,
        password_hash_outbound: PasswordHashOutboundPort,
        token_outbound: TokenOutboundPort,
        cache_outbound: CacheOutboundPort[RefreshTokenCacheValueVO],
    ) -> None:
        """Initializes the UserAuthenticationUseCase with the required dependencies.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The factory for
                creating loggers.
            unit_of_work (UserUnitOfWorkPort): The unit of work that manages
                the transaction boundary and exposes auth repositories.
            password_hash_outbound (PasswordHashOutboundPort): The service for hashing passwords.
            token_outbound (TokenOutboundPort): The service for generating
                access and refresh tokens.
            cache_outbound (CacheOutboundPort[RefreshTokenCacheValueVO]): The service for
                caching refresh tokens with associated user IDs and jti.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.unit_of_work = unit_of_work
        self.password_hash_outbound = password_hash_outbound
        self.token_outbound = token_outbound
        self.cache_outbound = cache_outbound

    async def execute(
        self, command: UserAuthenticationCommand
    ) -> UserAuthenticationResponse:
        """Execute the use case to use authentication.

        Opens a Unit of Work, checks whether the user exists, verifies the password,
        generates access and refresh tokens, stores the refresh token in cache, and
        commits — all within a single transaction.

        Args:
            command (UserAuthenticationCommand): The command containing the email
                and password for authentication.

        Returns:
            UserAuthenticationResponse: The response containing the access and refresh tokens.
        """
        self._logger.info("Executing user authentication use case", email=command.email)

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        email = EmailVO(command.email)
        plain_password = PlainPasswordVO(command.password)

        async with self.unit_of_work as uow:
            # Check if the user exists and verify the password
            user = await uow.users.find_by_email(email)
            if user is None:
                self._logger.warning("Authentication failed for email", email=email)
                raise AuthenticationFailedException()

            if not self.password_hash_outbound.verify(plain_password, user.password):
                self._logger.warning(
                    "Authentication failed for password", user_id=str(user.id)
                )
                raise AuthenticationFailedException()

            # Generate access and refresh tokens
            access_token_input = AccessTokenInputVO.create(user.id, user.role)
            access_token_response = self.token_outbound.generate_access(
                access_token_input
            )
            refresh_token_response = self.token_outbound.generate_refresh()

            # Build the cache entry for the refresh token
            key = RefreshTokenCacheKeyVO.from_token(
                refresh_token_response.refresh_token
            )
            ttl = CacheTTLVO(refresh_token_response.expires_in)
            value = RefreshTokenCacheValueVO.create(user.id)

            # Store the refresh token in cache with the associated user ID and jti
            entry = CacheEntryVO(key, ttl, value)
            await self.cache_outbound.set(entry)

        self._logger.info("User authenticated successfully", user_id=str(user.id))

        return UserAuthenticationResponse.response(
            access_token=str(access_token_response.access_token),
            access_token_type=access_token_response.token_type,
            access_expires_in=access_token_response.expires_in,
            refresh_token=str(refresh_token_response.refresh_token),
            refresh_expires_in=refresh_token_response.expires_in,
        )
