"""This module contains the TokenOutboundPort interface."""

from abc import ABC, abstractmethod

from src.shared.domain.value_objects.access_token_input_vo import AccessTokenInputVO
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.access_token_response_vo import (
    AccessTokenResponseVO,
)
from src.shared.domain.value_objects.refresh_token_response_vo import (
    RefreshTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class TokenOutboundPort(ABC):
    """Outbound port interface for token-related operations in the authentication domain."""

    @abstractmethod
    def generate_access(self, input: AccessTokenInputVO) -> AccessTokenResponseVO:
        """Generates a signed JWT access token.

        Args:
            input (AccessTokenInputVO): Value object containing sub and role.

        Returns:
            AccessTokenResponseVO: Value object containing access_token,
                token_type and expires_in.
        """
        pass

    @abstractmethod
    def generate_refresh(self) -> RefreshTokenResponseVO:
        """Generates an opaque refresh token.

        Returns:
            RefreshTokenResponseVO: Value object containing the opaque
                refresh_token string and expires_in seconds.
        """
        pass

    @abstractmethod
    def decode(self, token: TokenVO) -> AccessTokenPayloadVO:
        """Decodes a JWT access token and returns its verified payload.

        Args:
            token (TokenVO): The raw JWT string to decode and verify.

        Returns:
            AccessTokenPayloadVO: Value object with jti, sub, role and exp
                extracted from the token claims.
        """
        pass
