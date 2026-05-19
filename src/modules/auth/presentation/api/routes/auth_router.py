"""This module contains the routers for the auth module."""

from fastapi import APIRouter

from src.modules.auth.presentation.api.routes.user_authentication_router import (
    router as user_authentication_router,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication and Users"],
)

router.include_router(user_authentication_router)
