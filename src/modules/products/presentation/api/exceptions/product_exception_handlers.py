"""This module contains exception handlers for the products module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.domain.exceptions.product_exception import (
    InvalidProductNameException,
    InvalidUnitPriceException,
    ProductRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def product_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the product module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidProductNameException)
    async def invalid_product_name_exception_handler(
        request: Request, exc: InvalidProductNameException
    ) -> JSONResponse:
        """Handle InvalidProductNameException.

        Args:
            request (Request): The request object.
            exc (InvalidProductNameException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid product name exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            name=exc.name,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc), context={"name": exc.name}, details=exc.errors
                )
            ),
        )

    @app.exception_handler(InvalidUnitPriceException)
    async def invalid_unit_price_exception_handler(
        request: Request, exc: InvalidUnitPriceException
    ) -> JSONResponse:
        """Handle InvalidUnitPriceException.

        Args:
            request (Request): The request object.
            exc (InvalidUnitPriceException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid unit price exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors)
            ),
        )

    @app.exception_handler(ProductRepositoryException)
    async def product_repository_exception_handler(
        request: Request, exc: ProductRepositoryException
    ) -> JSONResponse:
        """Handle ProductRepositoryException.

        Args:
            request (Request): The request object.
            exc (ProductRepositoryException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "product repository exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error])
            ),
        )
