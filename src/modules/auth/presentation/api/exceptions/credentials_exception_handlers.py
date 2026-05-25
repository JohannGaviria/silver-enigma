"""This module contains exception handlers for the auth module."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
    InvalidNameException,
    InvalidPasswordHashException,
    InvalidPlainPasswordException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def credentials_exception_handlers(app: FastAPI) -> None:
    """Register all credentials exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(InvalidNameException)
    async def invalid_name_exception_handler(
        request: Request, exc: InvalidNameException
    ) -> JSONResponse:
        """Handle InvalidNameException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidNameException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid name exception occurred while processing request",
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

    @app.exception_handler(InvalidEmailException)
    async def invalid_email_exception_handler(
        request: Request, exc: InvalidEmailException
    ) -> JSONResponse:
        """Handle InvalidEmailException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidEmailException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid email exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            email=exc.email,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc), context={"email": exc.email}, details=exc.errors
                )
            ),
        )

    @app.exception_handler(InvalidPasswordHashException)
    async def invalid_password_hash_exception_handler(
        request: Request, exc: InvalidPasswordHashException
    ) -> JSONResponse:
        """Handle InvalidPasswordHashException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidPasswordHashException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid password hash exception occurred while processing request",
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

    @app.exception_handler(InvalidPlainPasswordException)
    async def invalid_plain_password_exception_handler(
        request: Request, exc: InvalidPlainPasswordException
    ) -> JSONResponse:
        """Handle InvalidPlainPasswordException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidPlainPasswordException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid plain password exception occurred while processing request",
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
