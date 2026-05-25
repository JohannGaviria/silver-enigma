"""This module contains cache exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions.cache_exception import (
    CacheDeletionException,
    CacheRetrievalException,
    CacheStorageException,
    InvalidCacheEntryException,
    InvalidCacheKeyException,
    InvalidCacheTTLException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def cache_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(InvalidCacheKeyException)
    async def invalid_cache_key_exception_handler(
        request: Request, exc: InvalidCacheKeyException
    ) -> JSONResponse:
        """Handle InvalidCacheKeyException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidCacheKeyException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid cache key exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidCacheTTLException)
    async def invalid_cache_ttl_exception_handler(
        request: Request, exc: InvalidCacheTTLException
    ) -> JSONResponse:
        """Handle InvalidCacheTTLException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidCacheTTLException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid cache ttl exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidCacheEntryException)
    async def invalid_cache_entry_exception_handler(
        request: Request, exc: InvalidCacheEntryException
    ) -> JSONResponse:
        """Handle InvalidCacheEntryException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidCacheEntryException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid cache entry exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )

    @app.exception_handler(CacheRetrievalException)
    async def cache_retrieval_exception_handler(
        request: Request, exc: CacheRetrievalException
    ) -> JSONResponse:
        """Handle CacheRetrievalException.

        Args:
            request (Request): The FastAPI request object.
            exc (CacheRetrievalException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "cache retrieval exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.errors]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(CacheStorageException)
    async def cache_storage_exception_handler(
        request: Request, exc: CacheStorageException
    ) -> JSONResponse:
        """Handle CacheStorageException.

        Args:
            request (Request): The FastAPI request object.
            exc (CacheStorageException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "cache storage exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.errors]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(CacheDeletionException)
    async def cache_deletion_exception_handler(
        request: Request, exc: CacheDeletionException
    ) -> JSONResponse:
        """Handle CacheDeletionException.

        Args:
            request (Request): The FastAPI request object.
            exc (CacheDeletionException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "cache deletion exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.errors]),
                exclude_none=True,
            ),
        )
