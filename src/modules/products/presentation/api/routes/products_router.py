"""This module contains the router for the products module."""

from fastapi import APIRouter

from src.modules.products.presentation.api.routes import (
    adjust_stock_router,
    create_product_router,
    get_product_catalog_router,
    get_warehouse_stock_router,
    toggle_product_status_router,
    update_product_router,
)

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


router.include_router(create_product_router.router)
router.include_router(update_product_router.router)
router.include_router(toggle_product_status_router.router)
router.include_router(adjust_stock_router.router)
router.include_router(get_warehouse_stock_router.router)
router.include_router(get_product_catalog_router.router)
