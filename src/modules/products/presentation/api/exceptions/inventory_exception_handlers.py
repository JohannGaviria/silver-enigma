"""This module contains the inventory exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.domain.exceptions.inventory_exception import (
    InventoryRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def inventory_exception_handlers(app: FastAPI) -> None:
    """Register the inventory exception handlers.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InventoryRepositoryException)
    async def inventory_exception_handler(
        request: Request, exc: InventoryRepositoryException
    ) -> JSONResponse:
        """Handle the InventoryRepositoryException.

        Args:
            request (Request): The request object.
            exc (InventoryRepositoryException): The InventoryRepositoryException instance.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "inventory repository exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error]),
                exclude_none=True,
            ),
        )
