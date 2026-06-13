"""This module contains the exception handlers for the warehouse module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.domain.exceptions.warehouse_referenced_order_exception import (
    InvalidWarehouseReferencedOrderException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def warehouse_referenced_order_exception_handlers(app: FastAPI) -> None:
    """Register the exception handlers for the warehouse module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidWarehouseReferencedOrderException)
    async def invalid_warehouse_referenced_order_exception_handler(
        request: Request, exc: InvalidWarehouseReferencedOrderException
    ) -> JSONResponse:
        """Handle the InvalidWarehouseReferencedOrderException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidWarehouseReferencedOrderException): The exception to handle.

        Returns:
            JSONResponse: A JSON response containing the error message.
        """
        _logger.error(
            "invalid warehouse referenced order exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error]),
                exclude_none=True,
            ),
        )
