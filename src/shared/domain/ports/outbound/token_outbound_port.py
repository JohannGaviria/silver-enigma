"""This module contains the TokenOutboundPort interface."""

from abc import ABC, abstractmethod

from src.shared.domain.value_objects.access_token_vo import AccessTokenVO
from src.shared.domain.value_objects.refresh_token_vo import RefreshTokenVO
from src.shared.domain.value_objects.token_payload_vo import TokenPayloadVO


class TokenOutboundPort(ABC):
    """Outbound port interface for token-related operations in the authentication domain."""

    @abstractmethod
    def access(self, payload: TokenPayloadVO) -> AccessTokenVO:
        """Generates an access token based on the provided payload.

        Args:
            payload (TokenPayloadVO): The payload containing the necessary
                information to generate the access token.

        Returns:
            AccessTokenVO: The generated access token value object.
        """
        pass

    @abstractmethod
    def refresh(self) -> RefreshTokenVO:
        """Generates a refresh token.

        Returns:
            RefreshTokenVO: The generated refresh token value object.
        """
        pass

    @abstractmethod
    def decode(self, token: AccessTokenVO) -> TokenPayloadVO:
        """Decodes an access token to extract the payload information.

        Args:
            token (AccessTokenVO): The access token to decode.

        Returns:
            TokenPayloadVO: The extracted payload information from the access token.
        """
        pass
