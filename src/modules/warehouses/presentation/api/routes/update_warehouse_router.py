"""This module contains the update warehouse router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.application.dtos.update_warehouse_dto import (
    UpdateWarehouseResponseDto,
)
from src.modules.warehouses.application.use_cases.update_warehouse_use_case import (
    UpdateWarehouseUseCase,
)
from src.modules.warehouses.presentation.api.compositions.use_case_composition import (
    get_update_warehouse_use_case,
)
from src.modules.warehouses.presentation.api.mappers.update_warehouse_mapper import (
    UpdateWarehouseApiMapper,
)
from src.modules.warehouses.presentation.api.schemas.update_warehouse_schema import (
    UpdateWarehouseRequestSchema,
    UpdateWarehouseResponseSchema,
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
    path="/{warehouse_id}",
    summary="Update warehouse.",
    description=(
        "Update the name and address of an existing warehouse. "
        "This endpoint validates ownership and permissions before "
        "persisting the changes and invalidating related cache entries."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[UpdateWarehouseResponseSchema],
            "description": "Warehouse updated successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid request data or business rule validation error.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication credentials were not provided or are invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The authenticated user does not have permission to update this warehouse.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def update_warehouse(
    warehouse_id: UUID,
    request: UpdateWarehouseRequestSchema,
    use_case: UpdateWarehouseUseCase = Depends(get_update_warehouse_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Update a warehouse.

    This endpoint updates the name and address of a warehouse
    and invalidates the cache for the warehouse by supplier.

    Args:
        warehouse_id (UUID): The ID of the warehouse to update.
        request (UpdateWarehouseRequestSchema): The request schema.
        use_case (UpdateWarehouseUseCase): The update warehouse use case.
        current_user (AccessTokenPayloadVO): The current user.

    Returns:
        JSONResponse: A JSON response containing the updated warehouse.
    """
    result: UpdateWarehouseResponseDto = await use_case.execute(
        command=UpdateWarehouseApiMapper.to_command(request, warehouse_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Warehouse updated successfully.",
                data=UpdateWarehouseApiMapper.to_response(result),
            )
        ),
    )
