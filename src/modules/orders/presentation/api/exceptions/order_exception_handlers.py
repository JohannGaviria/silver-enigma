"""This module contains the exception handlers for the Orders API."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.orders.domain.exceptions.order_exception import (
    DuplicateOrderItemsException,
    InactiveReferencedProductException,
    InvalidQuantityException,
    InvalidReferencedProductException,
    OrderItemsRequiredException,
    OrderRepositoryException,
    ProductsFromDifferentSuppliersException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def order_exception_handlers(app: FastAPI) -> None:
    """Register the exception handlers for the Orders API.

    Args:
        app (FastAPI): The FastAPI application.
    """

    @app.exception_handler(DuplicateOrderItemsException)
    async def duplicate_order_items_exception_handler(
        request: Request,
        exc: DuplicateOrderItemsException,
    ) -> JSONResponse:
        """Handle DuplicateOrderItemsException.

        Args:
            request (Request): The FastAPI request object.
            exc (DuplicateOrderItemsException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "duplicate order items exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InactiveReferencedProductException)
    async def inactive_referenced_product_exception_handler(
        request: Request,
        exc: InactiveReferencedProductException,
    ) -> JSONResponse:
        """Handle InactiveReferencedProductException.

        Args:
            request (Request): The FastAPI request object.
            exc (InactiveReferencedProductException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "inactive referenced product exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidQuantityException)
    async def invalid_quantity_exception_handler(
        request: Request,
        exc: InvalidQuantityException,
    ) -> JSONResponse:
        """Handle InvalidQuantityException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidQuantityException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid quantity exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
            quantity=exc.quantity,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                    context={"quantity": exc.quantity},
                    details=exc.errors,
                ),
            ),
        )

    @app.exception_handler(InvalidReferencedProductException)
    async def invalid_referenced_product_exception_handler(
        request: Request,
        exc: InvalidReferencedProductException,
    ) -> JSONResponse:
        """Handle InvalidReferencedProductException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidReferencedProductException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid referenced product exception occurred while processing request.",
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
                    details=exc.errors,
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(OrderItemsRequiredException)
    async def order_items_required_exception_handler(
        request: Request,
        exc: OrderItemsRequiredException,
    ) -> JSONResponse:
        """Handle OrderItemsRequiredException.

        Args:
            request (Request): The FastAPI request object.
            exc (OrderItemsRequiredException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "order items required exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(ProductsFromDifferentSuppliersException)
    async def products_from_different_suppliers_exception_handler(
        request: Request,
        exc: ProductsFromDifferentSuppliersException,
    ) -> JSONResponse:
        """Handle ProductsFromDifferentSuppliersException.

        Args:
            request (Request): The FastAPI request object.
            exc (ProductsFromDifferentSuppliersException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "products from different suppliers exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(OrderRepositoryException)
    async def order_repository_exception_handler(
        request: Request,
        exc: OrderRepositoryException,
    ) -> JSONResponse:
        """Handle OrderRepositoryException.

        Args:
            request (Request): The FastAPI request object.
            exc (OrderRepositoryException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "order repository exception occurred while processing request.",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)),
                exclude_none=True,
            ),
        )
