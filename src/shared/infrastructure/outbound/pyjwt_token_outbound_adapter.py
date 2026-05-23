"""This module contains the PyJWTTokenOutboundAdapter class."""

from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

import jwt

from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import (
    ExpiredTokenException,
    InvalidAccessTokenPayloadException,
    InvalidTokenException,
)
from src.shared.domain.ports.outbound.token_outbound_port import TokenOutboundPort
from src.shared.domain.value_objects.access_token_input_vo import AccessTokenInputVO
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.access_token_response_vo import (
    AccessTokenResponseVO,
)
from src.shared.domain.value_objects.refresh_token_response_vo import (
    RefreshTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class PyJWTTokenOutboundAdapter(TokenOutboundPort):
    """Adapter for generating and decoding JWT tokens using the PyJWT library."""

    def __init__(
        self,
        access_expires_in: int,
        refresh_expires_in: int,
        token_secret_key: str,
        token_algorithm: str,
    ) -> None:
        """Initializes the PyJWTTokenOutboundAdapter.

        Args:
            access_expires_in (int): The expiration time for access tokens in seconds.
            refresh_expires_in (int): The expiration time for refresh tokens in seconds.
            token_secret_key (str): The secret key used for encoding and decoding JWT tokens.
            token_algorithm (str): The algorithm used for encoding and decoding JWT tokens.
        """
        self.access_expires_in = access_expires_in
        self.refresh_expires_in = refresh_expires_in
        self.token_secret_key = token_secret_key
        self.token_algorithm = token_algorithm

    def _get_required_claim(self, payload: dict[str, object], key: str) -> object:
        """Retrieve a required claim from JWT payload.

        Extracts the value associated with the given claim key from the
        decoded JWT payload. If the claim is missing or its value is None,
        an InvalidAccessTokenPayloadException is raised.

        Args:
            payload (dict[str, object]): The decoded JWT payload.
            key (str): The claim name to retrieve.

        Returns:
            object: The value associated with the specified claim.

        Raises:
            InvalidAccessTokenPayloadException: If the claim is missing
                or its value is None.
        """
        value = payload.get(key)

        if value is None:
            raise InvalidAccessTokenPayloadException([f"Missing required claim: {key}"])

        return value

    def _generate(self, input: AccessTokenInputVO | None = None) -> TokenVO:
        """Generates a JWT token based on the provided input.

        Args:
            input (AccessTokenInputVO | None): The input data used to generate the token.
                If None, a token with an empty input will be generated.
        """
        # If no input is provided, generate a token with an empty input.
        # This can be used for generating refresh tokens that do not require specific claims.
        if input is None:
            return TokenVO(
                jwt.encode(
                    payload={},
                    key=self.token_secret_key,
                    algorithm=self.token_algorithm,
                )
            )

        # Generate the access token input with the provided
        # input data and set the expiration time.
        access_token_payload = AccessTokenPayloadVO(
            jti=input.jti,
            sub=input.sub,
            role=input.role,
            exp=datetime.now(UTC) + timedelta(seconds=self.access_expires_in),
        )
        return TokenVO(
            jwt.encode(
                access_token_payload.to_dict(),
                self.token_secret_key,
                self.token_algorithm,
            )
        )

    def generate_access(self, input: AccessTokenInputVO) -> AccessTokenResponseVO:
        """Generates an access token based on the provided input.

        Args:
            input (AccessTokenInputVO): The input data used to generate the access token.

        Returns:
            AccessTokenResponseVO: An object containing the generated access token,
                its type, and its expiration time.
        """
        access_token = self._generate(input)
        return AccessTokenResponseVO(
            access_token=access_token,
            token_type="Bearer",
            expires_in=self.access_expires_in,
        )

    def generate_refresh(self) -> RefreshTokenResponseVO:
        """Generates a refresh token and returns it in a RefreshTokenResponseVO.

        Returns:
            RefreshTokenResponseVO: An object containing the generated
                refresh token and its expiration time.
        """
        refresh_token = self._generate()
        return RefreshTokenResponseVO(
            refresh_token=refresh_token, expires_in=self.refresh_expires_in
        )

    def decode(self, token: TokenVO) -> AccessTokenPayloadVO:
        """Decodes a JWT token and returns the payload as an AccessTokenPayloadVO.

        Args:
            token (TokenVO): The JWT token to decode.

        Returns:
            AccessTokenPayloadVO: The decoded payload of the JWT token.
        """
        try:
            payload = jwt.decode(
                jwt=str(token),
                key=self.token_secret_key,
                algorithms=[self.token_algorithm],
            )
        except jwt.ExpiredSignatureError as e:
            raise ExpiredTokenException() from e

        except jwt.InvalidTokenError as e:
            raise InvalidTokenException(
                "The provided token is invalid or malformed."
            ) from e

        jti = self._get_required_claim(payload, "jti")
        sub = self._get_required_claim(payload, "sub")
        role = self._get_required_claim(payload, "role")
        exp = self._get_required_claim(payload, "exp")

        exp = cast(int | float, exp)

        return AccessTokenPayloadVO(
            jti=UUID(str(jti)),
            sub=UUID(str(sub)),
            role=UserRoleEnum(str(role)),
            exp=datetime.fromtimestamp(exp, UTC),
        )
