"""This module contains the security composition."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

from src.shared.domain.exceptions.exception import ExpiredTokenException
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.domain.value_objects.token_vo import TokenVO
from src.shared.infrastructure.outbound.pyjwt_token_outbound_adapter import (
    PyJWTTokenOutboundAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.compositions.infrastructure_composition import (
    get_logger_factory_outbound,
    get_token_outbound,
)

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    token_outbound: PyJWTTokenOutboundAdapter = Depends(get_token_outbound),
) -> AccessTokenPayloadVO:
    """Dependency injector to get the current user from the JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory.
        token_outbound (PyJWTTokenOutboundAdapter): The token outbound adapter.

    Returns:
        AccessTokenPayloadVO: The access token payload value object.

    Raises:
        ExpiredTokenException: If the token is expired.
    """
    _logger = logger_factory_outbound.get_logger(__name__)
    try:
        token = credentials.credentials
        payload = token_outbound.decode(TokenVO(token))
        _logger.info("Token decoded successfully", token=token, payload=payload)
        return AccessTokenPayloadVO(
            jti=payload.jti, sub=payload.sub, role=payload.role, exp=payload.exp
        )
    except PyJWTError as e:
        _logger.warning("Invalid or expired token", error=str(e))
        raise ExpiredTokenException() from e
