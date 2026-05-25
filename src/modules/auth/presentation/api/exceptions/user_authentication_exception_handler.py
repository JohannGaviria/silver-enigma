"""This module contains exception handlers for the user authentication endpoint."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.session_exception import (
    AuthenticationFailedException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def user_authentication_exception_handlers(app: FastAPI) -> None:
    """Register all user authentication exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AuthenticationFailedException)
    async def authentication_failed_exception_handler(
        request: Request, exc: AuthenticationFailedException
    ) -> JSONResponse:
        """Handle AuthenticationFailedException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

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
