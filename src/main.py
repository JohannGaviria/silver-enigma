"""This module contains the main application code for the FastAPI application."""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.modules.auth.presentation.api.exceptions.auth_exception_handler import (
    auth_exception_handlers,
)
from src.modules.auth.presentation.api.routes import auth_router
from src.modules.products.presentation.api.exceptions.inventory_exception_handlers import (
    inventory_exception_handlers,
)
from src.modules.products.presentation.api.exceptions.inventory_movement_exception_handlers import (
    inventory_movement_exception_handlers,
)
from src.modules.products.presentation.api.exceptions.inventory_warehouse_exception_handlers import (
    inventory_warehouse_exception_handlers,
)
from src.modules.products.presentation.api.exceptions.product_exception_handlers import (
    product_exception_handlers,
)
from src.modules.products.presentation.api.exceptions.product_referenced_order_exception_handlers import (
    product_referenced_order_exception_handlers,
)
from src.modules.products.presentation.api.exceptions.stock_exception_handlers import (
    stock_exception_handlers,
)
from src.modules.products.presentation.api.routes import products_router
from src.modules.warehouses.presentation.api.exceptions.warehouse_exception_handlers import (
    warehouse_exception_handlers,
)
from src.modules.warehouses.presentation.api.routes import warehouse_router
from src.shared.infrastructure.cache.redis_connection import RedisConnection
from src.shared.infrastructure.database.database_engine import DatabaseEngine
from src.shared.infrastructure.logging.structlog_configure_logging import (
    StructlogConfigureLogging,
)
from src.shared.presentation.api.exceptions.exception_handlers import exception_handlers
from src.shared.presentation.api.middleware.correlation_id_middleware import (
    CorrelationIdMiddleware,
)

app = FastAPI(
    title=settings.APP_NAME,
    summary=settings.APP_SUMMARY,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
)

# Configure logging using Structlog
StructlogConfigureLogging.configure(debug=settings.DEBUG)


allow_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOW_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Includes the middleware for the API endpoints
app.add_middleware(CorrelationIdMiddleware)


# Includes the exception handlers for the API endpoints
exception_handlers(app)
auth_exception_handlers(app)
warehouse_exception_handlers(app)
product_exception_handlers(app)
product_referenced_order_exception_handlers(app)
stock_exception_handlers(app)
inventory_movement_exception_handlers(app)
inventory_warehouse_exception_handlers(app)
inventory_exception_handlers(app)


# Includes the routers for the API endpoints
app.include_router(auth_router.router)
app.include_router(warehouse_router.router)
app.include_router(products_router.router)


@app.get(
    path="/",
    tags=["System"],
    summary="Root Endpoint",
    description="Returns a welcome message.",
)
async def root() -> JSONResponse:
    """Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return JSONResponse(
        content={"message": f"Welcome to the {settings.APP_NAME}!"},
        status_code=status.HTTP_200_OK,
    )


@app.get(
    path="/health",
    tags=["System"],
    summary="Health Check Endpoint",
    description="Checks the operational status of the server, PostgreSQL, and Redis.",
)
async def health_check() -> JSONResponse:
    """Health check endpoint that verifies the status of the server, PostgreSQL, and Redis.

    Returns:
        dict: A dictionary containing the health status of the services.
    """
    db_status = await DatabaseEngine.health_check()
    redis_status = await RedisConnection.health_check()

    payload = {
        "status": "healthy" if db_status and redis_status else "unhealthy",
        "database": db_status,
        "redis": redis_status,
    }

    status_code = (
        status.HTTP_200_OK
        if db_status and redis_status
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(content=payload, status_code=status_code)
