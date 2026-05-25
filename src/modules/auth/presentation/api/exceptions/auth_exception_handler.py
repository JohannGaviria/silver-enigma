"""This module contains exception handlers for the auth module."""

from fastapi import FastAPI

from src.modules.auth.presentation.api.exceptions.credentials_exception_handlers import (
    credentials_exception_handlers,
)
from src.modules.auth.presentation.api.exceptions.session_exception_handlers import (
    session_exception_handlers,
)
from src.modules.auth.presentation.api.exceptions.user_exception_handlers import (
    user_exception_handlers,
)


def auth_exception_handlers(app: FastAPI) -> None:
    """Register all auth exception handlers for the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    credentials_exception_handlers(app)
    user_exception_handlers(app)
    session_exception_handlers(app)
