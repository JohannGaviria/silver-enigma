"""This module contains the security composition."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, PyJWTError

from src.shared.domain.exceptions.token_exception import (
    AuthenticationTokenMissingException,
    ExpiredTokenException,
    InvalidTokenException,
)
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

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter = Depends(
        get_logger_factory_outbound
    ),
    token_outbound: PyJWTTokenOutboundAdapter = Depends(get_token_outbound),
) -> AccessTokenPayloadVO:
    """Dependency injector to get the current user from the JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials | None): The HTTP authorization credentials.
        logger_factory_outbound (StructlogLoggerFactoryOutboundAdapter): The logger factory.
        token_outbound (PyJWTTokenOutboundAdapter): The token outbound adapter.

    Returns:
        AccessTokenPayloadVO: The access token payload value object.

    Raises:
        ExpiredTokenException: If the token is expired.
    """
    _logger = logger_factory_outbound.get_logger(__name__)

    if credentials is None:
        _logger.warning("Authentication failed because no access token was provided.")
        raise AuthenticationTokenMissingException()

    try:
        token = credentials.credentials
        payload = token_outbound.decode(TokenVO(token))
        _logger.info("Token decoded successfully", token=token, payload=payload)
        return AccessTokenPayloadVO(
            jti=payload.jti, sub=payload.sub, role=payload.role, exp=payload.exp
        )
    except ExpiredSignatureError as exc:
        _logger.warning(
            "Authentication failed due to an expired token", exc_info=str(exc)
        )
        raise ExpiredTokenException() from exc
    except PyJWTError as exc:
        _logger.warning(
            "Authentication failed because the access token is invalid.",
            exc_info=str(exc),
        )
        raise InvalidTokenException(
            "The access token is invalid or malformed."
        ) from exc
