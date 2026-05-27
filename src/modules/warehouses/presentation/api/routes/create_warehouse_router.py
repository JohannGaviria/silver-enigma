"""This module contains the create warehouse router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.application.dtos.create_warehouse_dto import (
    CreateWarehouseResponseDto,
)
from src.modules.warehouses.application.use_cases.create_warehouse_use_case import (
    CreateWarehouseUseCase,
)
from src.modules.warehouses.presentation.api.compositions.use_case_composition import (
    get_create_warehouse_use_case,
)
from src.modules.warehouses.presentation.api.mappers.create_warehouse_mapper import (
    CreateWarehouseApiMapper,
)
from src.modules.warehouses.presentation.api.schemas.create_warehouse_schema import (
    CreateWarehouseRequestSchema,
)
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.compositions.security_composition import (
    get_current_user,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)

router = APIRouter()


@router.post(
    path="/",
    summary="Create a new warehouse for a supplier.",
    description=(
        "Creates a new warehouse associated with the authenticated supplier. "
        "Only users with the SUPPLIER role are allowed to perform this action. "
        "The request validates the warehouse data before persisting it in the system."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[CreateWarehouseResponseDto],
            "description": "The warehouse was created successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "The request was invalid.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "The request was unauthorized.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The request was forbidden.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "The request was invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An internal server error occurred.",
        },
    },
)
async def create_warehouse(
    request: CreateWarehouseRequestSchema,
    use_case: CreateWarehouseUseCase = Depends(get_create_warehouse_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Create a new warehouse for a supplier.

    This endpoint allows a supplier to create a new warehouse in the system
    associated with their account. The request is validated before being
    persisted in the database.

    Args:
        request (CreateWarehouseRequestSchema): The request schema containing
            the warehouse data.
        use_case (CreateWarehouseUseCase): The use case for creating a warehouse.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: A JSON response containing the warehouse created.
    """
    result: CreateWarehouseResponseDto = await use_case.execute(
        CreateWarehouseApiMapper.to_command(request, supplier_id=current_user.sub)
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Warehouse created successfully.",
                data=CreateWarehouseApiMapper.to_response(result),
            )
        ),
    )
