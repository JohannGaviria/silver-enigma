"""This module contains exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.exceptions.cache_exception_handlers import (
    cache_exception_handlers,
)
from src.shared.presentation.api.exceptions.token_exception_handlers import (
    token_exception_handlers,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    token_exception_handlers(app)
    cache_exception_handlers(app)

    @app.exception_handler(Exception)
    async def internal_server_error_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle Exception for internal server error.

        Args:
            request (Request): The FastAPI request object.
            exc (Exception): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "Unhandled exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)), exclude_none=True
            ),
        )
