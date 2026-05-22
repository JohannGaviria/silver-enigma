"""This module contains the routers for the auth module."""

from fastapi import APIRouter

from src.modules.auth.presentation.api.routes import (
    admin_user_registration_router,
    user_authentication_router,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication and Users"],
)

router.include_router(user_authentication_router.router)
router.include_router(admin_user_registration_router.router)
