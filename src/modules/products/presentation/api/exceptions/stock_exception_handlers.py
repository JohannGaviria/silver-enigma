"""This module contains the stock exception handler for the products module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidAvailableStockException,
    InvalidTotalStockException,
    StockConflictException,
    StockRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def stock_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the product module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidTotalStockException)
    async def invalid_total_stock_exception_handler(
        request: Request, exc: InvalidTotalStockException
    ) -> JSONResponse:
        """Handle InvalidTotalStockException.

        Args:
            request (Request): The request object.
            exc (InvalidTotalStockException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid total stock exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            total_stock=exc.total_stock,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    context={"total_stock": exc.total_stock},
                    details=exc.errors,
                )
            ),
        )

    @app.exception_handler(InvalidAvailableStockException)
    async def invalid_available_stock_exception_handler(
        request: Request, exc: InvalidAvailableStockException
    ) -> JSONResponse:
        """Handle InvalidAvailableStockException.

        Args:
            request (Request): The request object.
            exc (InvalidAvailableStockException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid available stock exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    context={"available_stock": exc.available_stock},
                    details=exc.errors,
                )
            ),
        )

    @app.exception_handler(StockConflictException)
    async def stock_conflict_exception_handler(
        request: Request, exc: StockConflictException
    ) -> JSONResponse:
        """Handle StockConflictException.

        Args:
            request (Request): The request object.
            exc (StockConflictException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "stock conflict exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            product_id=exc.product_id,
            warehouse_id=exc.warehouse_id,
            requested_quantity=exc.requested_quantity,
            available_stock=exc.available_stock,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    context={
                        "product_id": exc.product_id,
                        "warehouse_id": exc.warehouse_id,
                        "requested_quantity": exc.requested_quantity,
                        "available_stock": exc.available_stock,
                    },
                )
            ),
        )

    @app.exception_handler(StockRepositoryException)
    async def stock_repository_exception_handler(
        request: Request, exc: StockRepositoryException
    ) -> JSONResponse:
        """Handle StockRepositoryException.

        Args:
            request (Request): The request object.
            exc (StockRepositoryException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "stock repository exception occurred while processing request",
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
