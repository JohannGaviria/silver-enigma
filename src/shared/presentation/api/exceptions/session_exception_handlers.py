"""This module contains session exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def as_session_exception_handlers(app: FastAPI) -> None:
    """Register all session exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

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
