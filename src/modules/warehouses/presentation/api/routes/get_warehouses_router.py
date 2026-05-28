"""This module contains the router for the get warehouses API."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.warehouses.application.dtos.get_warehouses_dto import (
    GetWarehousesResponseDto,
)
from src.modules.warehouses.application.use_cases.get_warehouses_use_case import (
    GetWarehousesUseCase,
)
from src.modules.warehouses.presentation.api.compositions.use_case_composition import (
    get_get_warehouses_use_case,
)
from src.modules.warehouses.presentation.api.mappers.get_warehouses_mapper import (
    GetWarehousesApiMapper,
)
from src.modules.warehouses.presentation.api.schemas.get_warehouses_schema import (
    GetWarehousesResponseSchema,
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
    path="/",
    summary="Obtain authenticated supplier user warehouses.",
    description="Obtain the warehouses of the authenticated supplier user.",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[GetWarehousesResponseSchema],
            "description": "Successfully retrieved warehouses.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Unauthorized. The user is not authenticated.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "Forbidden. The user is not authorized to access this resource.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal Server Error.",
        },
    },
)
async def get_warehouses(
    use_case: GetWarehousesUseCase = Depends(get_get_warehouses_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Get warehouses.

    This endpoint retrieves the warehouses of the authenticated supplier user.

    Args:
        use_case (GetWarehousesUseCase): The GetWarehousesUseCase instance.
        current_user (AccessTokenPayloadVO): The AccessTokenPayloadVO instance.

    Returns:
        JSONResponse: A JSON response containing the warehouses.
    """
    result: GetWarehousesResponseDto = await use_case.execute(
        AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        )
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Successfully retrieved warehouses.",
                data=GetWarehousesApiMapper.to_response(result),
            )
        ),
    )
