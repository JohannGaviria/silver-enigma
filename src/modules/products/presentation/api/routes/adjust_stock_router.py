"""This module contains the adjust stock router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.adjust_stock_dto import (
    AdjustStockResponseDto,
)
from src.modules.products.application.use_cases.adjust_stock_use_case import (
    AdjustStockUseCase,
)
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_adjust_stock_use_case,
)
from src.modules.products.presentation.api.mappers.adjust_stock_mapper import (
    AdjustStockApiMapper,
)
from src.modules.products.presentation.api.schemas.adjust_stock_schema import (
    AdjustStockRequestSchema,
    AdjustStockResponseSchema,
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


@router.put(
    path="/{product_id}/warehouses/{warehouse_id}/stock",
    summary="Adjust product stock",
    description=(
        "Adjusts the stock quantity of a product in a specific warehouse. "
        "The operation creates an inventory movement record and updates the "
        "reserved stock accordingly."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[AdjustStockResponseSchema],
            "description": "Stock adjusted successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid stock adjustment request.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "Product or warehouse not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": (
                "The stock adjustment cannot be completed due to a business rule conflict."
            ),
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Request validation failed.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication credentials were not provided or are invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "Insufficient permissions to adjust stock.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An unexpected error occurred while adjusting stock.",
        },
    },
)
async def adjust_stock(
    request: AdjustStockRequestSchema,
    product_id: UUID,
    warehouse_id: UUID,
    use_case: AdjustStockUseCase = Depends(get_adjust_stock_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Adjust product stock.

    This endpoint adjusts the stock level of a product in a specific warehouse
    by registering an auditable inventory movement and updating the reserved
    stock accordingly.

    Args:
        request (AdjustStockRequestSchema): The request schema.
        product_id (UUID): The ID of the product.
        warehouse_id (UUID): The ID of the warehouse.
        use_case (AdjustStockUseCase): The adjust stock use case.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: A JSON response containing the adjusted stock.
    """
    result: AdjustStockResponseDto = await use_case.execute(
        command=AdjustStockApiMapper.to_command(request, product_id, warehouse_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Stock adjusted successfully.",
                data=AdjustStockApiMapper.to_response(result),
            )
        ),
    )
