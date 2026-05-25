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
from src.modules.auth.domain.exceptions.session_exception import (
    InvalidRefreshTokenCacheValueException,
)
from src.modules.auth.domain.exceptions.user_exception import (
    UserAlreadyExistsException,
    UserNotFoundException,
    UserRepositoryException,
)
from src.modules.auth.presentation.api.exceptions.admin_user_registration_exception_handler import (
    admin_user_registration_exception_handlers,
)
from src.modules.auth.presentation.api.exceptions.reissue_session_credentials_exception_handler import (
    reissue_session_credentials_exception_handlers,
)
from src.modules.auth.presentation.api.exceptions.user_authentication_exception_handler import (
    user_authentication_exception_handlers,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

logger = StructlogLoggerFactoryOutboundAdapter()
_logger = logger.get_logger(__name__)


def auth_exception_handlers(app: FastAPI) -> None:
    """Register all auth exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    user_authentication_exception_handlers(app)
    admin_user_registration_exception_handlers(app)
    reissue_session_credentials_exception_handlers(app)

    @app.exception_handler(InvalidNameException)
    async def invalid_name_exception_handler(
        request: Request, exc: InvalidNameException
    ) -> JSONResponse:
        """Handle InvalidNameException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

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
            request: The FastAPI request object.
            exc: The exception instance.

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
            request: The FastAPI request object.
            exc: The exception instance.

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
            request: The FastAPI request object.
            exc: The exception instance.

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

    @app.exception_handler(UserRepositoryException)
    async def user_repository_exception_handler(
        request: Request, exc: UserRepositoryException
    ) -> JSONResponse:
        """Handle UserRepositoryException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "user repository exception occurred while processing request",
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

    @app.exception_handler(UserAlreadyExistsException)
    async def user_already_exists_exception_handler(
        request: Request, exc: UserAlreadyExistsException
    ) -> JSONResponse:
        """Handle UserAlreadyExistsException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "user already exists exception occurred while processing request",
            request_method=request.method,
            request_url=request.url.path,
            exception_message=exc,
            errors=exc.errors,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                ErrorsResponseSchema(message=str(exc), details=[exc.errors]),
                exclude_none=True,
            ),
        )

    @app.exception_handler(InvalidRefreshTokenCacheValueException)
    async def invalid_refresh_token_cache_value_exception_handler(
        request: Request, exc: InvalidRefreshTokenCacheValueException
    ) -> JSONResponse:
        """Handle InvalidRefreshTokenCacheValueException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

        Returns:
            JSONResponse with error details.
        """
        _logger.error(
            "invalid refresh token cache value exception occurred while processing request",
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

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_exception_handler(
        request: Request, exc: UserNotFoundException
    ) -> JSONResponse:
        """Handle UserNotFoundException.

        Args:
            request: The FastAPI request object.
            exc: The exception instance.

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
