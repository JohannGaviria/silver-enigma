"""This module contains the toggle product status router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.toggle_product_status_dto import (
    ToggleProductStatusResponseDto,
)
from src.modules.products.application.use_cases.toggle_product_status_use_case import (
    ToggleProductStatusUseCase,
)
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_toggle_product_status_use_case,
)
from src.modules.products.presentation.api.mappers.toggle_product_status_mapper import (
    ToggleProductStatusApiMapper,
)
from src.modules.products.presentation.api.schemas.toggle_product_status_schema import (
    ToggleProductStatusRequestSchema,
    ToggleProductStatusResponseSchema,
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
    path="/{product_id}/status",
    summary="Toggle the status of a product.",
    description=(
        "Toggle the status of a product. The request must include the "
        "optional values to be updated."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[ToggleProductStatusResponseSchema],
            "description": "The product was toggled successfully.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "The request was not authenticated.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "The request was authenticated but lacked sufficient permissions.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": "The product with the given ID was not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "The product is referenced by an order.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "The request was invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An unexpected error occurred.",
        },
    },
)
async def toggle_product_status(
    product_id: UUID,
    request: ToggleProductStatusRequestSchema,
    use_case: ToggleProductStatusUseCase = Depends(get_toggle_product_status_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Toggle the status of a product.

    This endpoint toggles the status of an existing product with the provided ID.

    Args:
        product_id (UUID): The ID of the product to toggle the status of.
        request (ToggleProductStatusRequestSchema): The request schema containing the new status.
        use_case (ToggleProductStatusUseCase): The ToggleProductStatusUseCase instance.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: A JSON response containing the updated product.
    """
    result: ToggleProductStatusResponseDto = await use_case.execute(
        command=ToggleProductStatusApiMapper.to_command(request, product_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub,
            role=current_user.role,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Product status toggled successfully.",
                data=ToggleProductStatusApiMapper.to_response(result),
            )
        ),
    )
