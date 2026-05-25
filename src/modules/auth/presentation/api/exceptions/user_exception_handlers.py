"""This module contains user exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.user_exception import (
    AdminAlreadyExistsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserRepositoryException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def user_exception_handlers(app: FastAPI) -> None:
    """Register all user exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_exception_handler(
        request: Request, exc: UserNotFoundException
    ) -> JSONResponse:
        """Handle UserNotFoundException.

        Args:
            request (Request): The FastAPI request object.
            exc (UserNotFoundException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "user not found exception occurred while processing request",
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

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExistsException
    ) -> JSONResponse:
        """Handle UserAlreadyExistsException.

        Args:
            request (Request): The FastAPI request object.
            exc (UserAlreadyExistsException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "user already exists exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(AdminAlreadyExistsException)
    async def admin_already_exists_exception_handler(
        request: Request, exc: AdminAlreadyExistsException
    ) -> JSONResponse:
        """Handle AdminAlreadyExistsException.

        Args:
            request (Request): The FastAPI request object.
            exc (AdminAlreadyExistsException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "admin already exists exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc)),
                exclude_none=True,
            ),
        )

    @app.exception_handler(UserRepositoryException)
    async def user_repository_exception_handler(
        request: Request, exc: UserRepositoryException
    ) -> JSONResponse:
        """Handle UserRepositoryException.

        Args:
            request (Request): The FastAPI request object.
            exc (UserRepositoryException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "user repository exception occurred while processing request",
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
