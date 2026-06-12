"""This module contains exception handlers for the products module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.domain.exceptions.product_referenced_order_exception import (
    InvalidProductReferencedOrderException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def product_referenced_order_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the product module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidProductReferencedOrderException)
    async def invalid_product_referenced_order_exception_handler(
        request: Request, exc: InvalidProductReferencedOrderException
    ) -> JSONResponse:
        """Handle InvalidProductReferencedOrderException.

        Args:
            request (Request): The request object.
            exc (InvalidProductReferencedOrderException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid product referenced order exception occurred while processing request.",
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
