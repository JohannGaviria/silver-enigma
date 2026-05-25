"""This module contains exception handlers for the auth module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.session_exception import (
    AuthenticationFailedException,
    InsufficientPermissionsException,
    InvalidRefreshTokenCacheValueException,
    SessionNotFoundException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def session_exception_handlers(app: FastAPI) -> None:
    """Register all session exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(SessionNotFoundException)
    async def session_not_found_exception_handler(
        request: Request, exc: SessionNotFoundException
    ) -> JSONResponse:
        """Handle SessionNotFoundException.

        Args:
            request (Request): The FastAPI request object.
            exc (SessionNotFoundException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "session not found exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)),
                exclude_none=True,
            ),
        )

    @app.exception_handler(AuthenticationFailedException)
    async def authentication_failed_exception_handler(
        request: Request, exc: AuthenticationFailedException
    ) -> JSONResponse:
        """Handle AuthenticationFailedException.

        Args:
            request (Request): The FastAPI request object.
            exc (AuthenticationFailedException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "authentication failed exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)), exclude_none=True
            ),
        )

    @app.exception_handler(InsufficientPermissionsException)
    async def insufficient_permissions_exception_handler(
        request: Request, exc: InsufficientPermissionsException
    ) -> JSONResponse:
        """Handle InsufficientPermissionsException.

        Args:
            request (Request): The FastAPI request object.
            exc (InsufficientPermissionsException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "insufficient permissions exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidRefreshTokenCacheValueException)
    async def invalid_refresh_token_cache_value_exception_handler(
        request: Request, exc: InvalidRefreshTokenCacheValueException
    ) -> JSONResponse:
        """Handle InvalidRefreshTokenCacheValueException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidRefreshTokenCacheValueException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid refresh token cache value exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )
