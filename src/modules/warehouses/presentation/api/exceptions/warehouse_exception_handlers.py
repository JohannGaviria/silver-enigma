"""This module contains the exception handlers for the warehouse module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseAddressException,
    InvalidWarehouseNameException,
    WarehouseNotFoundException,
    WarehouseRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def warehouse_exception_handlers(app: FastAPI) -> None:
    """Register the exception handlers for the warehouse module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(InvalidWarehouseNameException)
    async def invalid_warehouse_name_exception_handler(
        request: Request, exc: InvalidWarehouseNameException
    ) -> JSONResponse:
        """Handle the InvalidWarehouseNameException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidWarehouseNameException): The exception to handle.

        Returns:
            JSONResponse: A JSON response containing the error message.
        """
        _logger.error(
            "invalid warehouse name exception occurred while processing request",
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

    @app.exception_handler(InvalidWarehouseAddressException)
    async def invalid_warehouse_address_exception_handler(
        request: Request, exc: InvalidWarehouseAddressException
    ) -> JSONResponse:
        """Handle the InvalidWarehouseAddressException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidWarehouseAddressException): The exception to handle.

        Returns:
            JSONResponse: A JSON response containing the error message.
        """
        _logger.error(
            "invalid warehouse address exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            address=exc.address,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    context={"address": exc.address},
                    details=exc.errors,
                )
            ),
        )

    @app.exception_handler(WarehouseRepositoryException)
    async def warehouse_repository_exception_handler(
        request: Request, exc: WarehouseRepositoryException
    ) -> JSONResponse:
        """Handle the WarehouseRepositoryException.

        Args:
            request (Request): The FastAPI request object.
            exc (WarehouseRepositoryException): The exception to handle.

        Returns:
            JSONResponse: A JSON response containing the error message.
        """
        _logger.error(
            "warehouse repository exception occurred while processing request",
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

    @app.exception_handler(WarehouseNotFoundException)
    async def warehouse_not_found_exception_handler(
        request: Request, exc: WarehouseNotFoundException
    ) -> JSONResponse:
        """Handle the WarehouseNotFoundException.

        Args:
            request (Request): The FastAPI request object.
            exc (WarehouseNotFoundException): The exception to handle.

        Returns:
            JSONResponse: A JSON response containing the error message.
        """
        _logger.error(
            "warehouse not found exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)),
                exclude_none=True,
            ),
        )
