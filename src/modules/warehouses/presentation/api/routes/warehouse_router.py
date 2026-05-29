"""This module contains the router for the warehouses API."""

from fastapi import APIRouter

from src.modules.warehouses.presentation.api.routes import (
    create_warehouse_router,
    get_warehouses_router,
    update_warehouse_router,
)

router = APIRouter(
    prefix="/api/v1/warehouses",
    tags=["Warehouses"],
)

router.include_router(create_warehouse_router.router)
router.include_router(get_warehouses_router.router)
router.include_router(update_warehouse_router.router)
