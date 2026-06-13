"""This module contains the toggle warehouse status router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.application.dtos.toggle_warehouse_status_dto import (
    ToggleWarehouseStatusResponseDto,
)
from src.modules.warehouses.application.use_cases.toggle_warehouse_status_use_case import (
    ToggleWarehouseStatusUseCase,
)
from src.modules.warehouses.presentation.api.compositions.use_case_composition import (
    get_toggle_warehouse_status_use_case,
)
from src.modules.warehouses.presentation.api.mappers.toggle_warehouse_status_mapper import (
    ToggleWarehouseStatusApiMapper,
)
from src.modules.warehouses.presentation.api.schemas.toggle_warehouse_status_schema import (
    ToggleWarehouseStatusRequestSchema,
    ToggleWarehouseStatusResponseSchema,
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


@router.patch(
    path="/{warehouse_id}/status",
    summary="Toggle warehouse status.",
    description=(
        "Toggle the status of an existing warehouse. "
        "This endpoint toggles the active status of a warehouse and"
        "invalidates the cache for the warehouse by supplier."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[ToggleWarehouseStatusResponseSchema],
            "description": "Warehouse status toggled successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid request data or business rule validation error.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "Warehouse not found.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication credentials were not provided or are invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user does not have permission to toggle this warehouse.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "The warehouse has active orders.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def toggle_warehouse_status(
    warehouse_id: UUID,
    request: ToggleWarehouseStatusRequestSchema,
    use_case: ToggleWarehouseStatusUseCase = Depends(
        get_toggle_warehouse_status_use_case
    ),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Toggle the status of a warehouse.

    This endpoint toggles the active status of a warehouse and invalidates the cache for the warehouse by supplier.

    Args:
        warehouse_id (UUID): The ID of the warehouse to toggle.
        request (ToggleWarehouseStatusRequestSchema): The request schema.
        use_case (ToggleWarehouseStatusUseCase): The toggle warehouse status use case.
        current_user (AccessTokenPayloadVO): The current user.

    Returns:
        JSONResponse: A JSON response containing the updated warehouse.
    """
    result: ToggleWarehouseStatusResponseDto = await use_case.execute(
        command=ToggleWarehouseStatusApiMapper.to_command(request, warehouse_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Warehouse status toggled successfully.",
                data=ToggleWarehouseStatusApiMapper.to_response(result),
            )
        ),
    )
