"""This module contains exception handlers for the user authentication endpoint."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.session_exception import (
    SessionNotFoundException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def reissue_session_credentials_exception_handlers(app: FastAPI) -> None:
    """Register all reissue session credentials exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(SessionNotFoundException)
    async def session_not_found_exception_handler(
        request: Request, exc: SessionNotFoundException
    ) -> JSONResponse:
        """Handle SessionNotFoundException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

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
