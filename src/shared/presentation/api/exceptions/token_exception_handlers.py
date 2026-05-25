"""This module contains token exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions.token_exception import (
    AuthenticationTokenMissingException,
    ExpiredTokenException,
    InvalidAccessTokenInputException,
    InvalidAccessTokenPayloadException,
    InvalidAccessTokenResponseException,
    InvalidRefreshTokenInputException,
    InvalidRefreshTokenResponseException,
    InvalidTokenException,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def token_exception_handlers(app: FastAPI) -> None:
    """Register all token exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(InvalidAccessTokenPayloadException)
    async def invalid_access_token_payload_exception_handler(
        request: Request, exc: InvalidAccessTokenPayloadException
    ) -> JSONResponse:
        """Handle InvalidAccessTokenPayloadException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidAccessTokenPayloadException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid access token payload exception occurred while processing request",
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

    @app.exception_handler(InvalidAccessTokenInputException)
    async def invalid_access_token_input_exception_handler(
        request: Request, exc: InvalidAccessTokenInputException
    ) -> JSONResponse:
        """Handle InvalidAccessTokenInputException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidAccessTokenInputException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid access token input exception occurred while processing request",
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

    @app.exception_handler(InvalidAccessTokenResponseException)
    async def invalid_access_token_response_exception_handler(
        request: Request, exc: InvalidAccessTokenResponseException
    ) -> JSONResponse:
        """Handle InvalidAccessTokenResponseException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidAccessTokenResponseException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid access token response exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidRefreshTokenInputException)
    async def invalid_refresh_token_input_exception_handler(
        request: Request, exc: InvalidRefreshTokenInputException
    ) -> JSONResponse:
        """Handle InvalidRefreshTokenInputException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidRefreshTokenInputException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid refresh token input exception occurred while processing request",
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

    @app.exception_handler(InvalidRefreshTokenResponseException)
    async def invalid_refresh_token_response_exception_handler(
        request: Request, exc: InvalidRefreshTokenResponseException
    ) -> JSONResponse:
        """Handle InvalidRefreshTokenResponseException.

        Args:
            request (Request): The FastAPI request object.
            exc (InvalidRefreshTokenResponseException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid refresh token response exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=exc.errors),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidTokenException)
    async def invalid_token_exception_handler(
        request: Request, exc: InvalidTokenException
    ) -> JSONResponse:
        """Handle InvalidTokenException.

        Args:
            request  (Request): The FastAPI request object.
            exc (InvalidTokenException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid token exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            error=exc.error,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.error]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(ExpiredTokenException)
    async def expired_token_exception_handler(
        request: Request, exc: ExpiredTokenException
    ) -> JSONResponse:
        """Handle ExpiredTokenException.

        Args:
            request (Request): The FastAPI request object.
            exc (ExpiredTokenException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "expired token exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )

    @app.exception_handler(AuthenticationTokenMissingException)
    async def authentication_token_missing_exception(
        request: Request, exc: AuthenticationTokenMissingException
    ) -> JSONResponse:
        """Handle AuthenticationTokenMissingException.

        Args:
            request (Request): The FastAPI request object.
            exc (AuthenticationTokenMissingException): The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "authentication token missing exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                ErrorsResponseSchema(
                    message=str(exc),
                ),
                exclude_none=True,
            ),
        )
