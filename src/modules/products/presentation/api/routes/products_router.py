"""This module contains the router for the products module."""

from fastapi import APIRouter

from src.modules.products.presentation.api.routes import (
    create_product_router,
    update_product_router,
)

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


router.include_router(create_product_router.router)
router.include_router(update_product_router.router)
