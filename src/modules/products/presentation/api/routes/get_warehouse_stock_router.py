"""This module contains the router for the get warehouse stock endpoint."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.get_warehouse_stock_dto import (
    GetWarehouseStockResponseDto,
)
from src.modules.products.application.use_cases.get_warehouse_stock_use_case import (
    GetWarehouseStockUseCase,
)
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_get_warehouse_stock_use_case,
)
from src.modules.products.presentation.api.mappers.get_warehouse_stock_mapper import (
    GetWarehouseStockApiMapper,
)
from src.modules.products.presentation.api.schemas.get_warehouse_stock_schema import (
    GetWarehouseStockResponseSchema,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.compositions.security_composition import (
    get_current_user,
)
from src.shared.presentation.api.mappers.authenticated_user_mapper import (
    AuthenticatedUserApiMapper,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)

router = APIRouter()


@router.get(
    path="/warehouses/{warehouse_id}/stock",
    summary="Retrieve warehouse stock inventory.",
    description=(
        "Retrieves the paginated stock inventory for a specific warehouse, "
        "including product availability, quantities, and stock-related information."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[GetWarehouseStockResponseSchema],
            "description": ("Warehouse stock inventory retrieved successfully."),
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": (
                "Invalid request parameters. This may occur when the warehouse ID "
                "is invalid or pagination parameters are outside the allowed range."
            ),
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": (
                "Authentication credentials were not provided or are invalid."
            ),
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": (
                "The authenticated user does not have permission to access "
                "the requested warehouse stock information."
            ),
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": (
                "An unexpected error occurred while retrieving the warehouse stock."
            ),
        },
    },
)
async def get_warehouse_stock(
    warehouse_id: UUID,
    page: int = Query(default=1, ge=1, description="Page number to retrieve."),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of stock records returned per page.",
    ),
    use_case: GetWarehouseStockUseCase = Depends(get_get_warehouse_stock_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Get warehouse stock endpoint.

    Retrieves a paginated list of stock items stored in the specified warehouse.
    The response includes inventory information such as available stock quantities
    and related product details.

    Args:
        warehouse_id (UUID): Unique identifier of the warehouse whose stock will be retrieved.
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of records returned per page. Defaults to 10.
        use_case (GetWarehouseStockUseCase): Application use case responsible for retrieving warehouse stock data.
        current_user (AccessTokenPayloadVO): Authenticated user requesting the information.

    Returns:
        JSONResponse: A successful response containing the paginated warehouse stock inventory.
    """
    result: GetWarehouseStockResponseDto = await use_case.execute(
        command=GetWarehouseStockApiMapper.to_command(warehouse_id, page, page_size),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Warehouse stock inventory retrieved successfully.",
                data=GetWarehouseStockApiMapper.to_response(result),
            )
        ),
    )
