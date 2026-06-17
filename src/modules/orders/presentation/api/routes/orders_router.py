"""This module contains the Order API routes."""

from fastapi import APIRouter

from src.modules.orders.presentation.api.routes import create_order_router

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)

router.include_router(create_order_router.router)
