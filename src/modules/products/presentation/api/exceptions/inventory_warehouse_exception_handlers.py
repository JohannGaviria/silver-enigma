"""This module contains the inventory warehouse exception handler for the products module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.domain.exceptions.inventory_warehouse_exception import (
    InvalidReferencedWarehouseException,
    ReferencedWarehouseNotActiveException,
    ReferencedWarehouseNotFoundException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def inventory_warehouse_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the product module.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(ReferencedWarehouseNotFoundException)
    async def referenced_warehouse_not_found_exception_handler(
        request: Request, exc: ReferencedWarehouseNotFoundException
    ) -> JSONResponse:
        """Handle ReferencedWarehouseNotFoundException.

        Args:
            request (Request): The request object.
            exc (ReferencedWarehouseNotFoundException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "referenced warehouse not found exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)), exclude_none=True
            ),
        )

    @app.exception_handler(ReferencedWarehouseNotActiveException)
    async def referenced_warehouse_not_active_exception_handler(
        request: Request, exc: ReferencedWarehouseNotActiveException
    ) -> JSONResponse:
        """Handle ReferencedWarehouseNotActiveException.

        Args:
            request (Request): The request object.
            exc (ReferencedWarehouseNotActiveException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "referenced warehouse not active exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)), exclude_none=True
            ),
        )

    @app.exception_handler(InvalidReferencedWarehouseException)
    async def invalid_referenced_warehouse_exception_handler(
        request: Request, exc: InvalidReferencedWarehouseException
    ) -> JSONResponse:
        """Handle InvalidReferencedWarehouseException.

        Args:
            request (Request): The request object.
            exc (InvalidReferencedWarehouseException): The exception to handle.

        Returns:
            JSONResponse: A JSON response with the error message.
        """
        _logger.error(
            "invalid referenced warehouse exception occurred while processing request",
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
                    context={"warehouse_id": exc.warehouse_id},
                    details=exc.errors,
                )
            ),
        )
