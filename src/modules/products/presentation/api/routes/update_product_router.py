"""This module contains the update product router."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.update_product_dto import (
    UpdatedProductResponseDto,
)
from src.modules.products.application.use_cases.update_product_use_case import (
    UpdateProductUseCase,
)
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_update_product_use_case,
)
from src.modules.products.presentation.api.mappers.update_product_mapper import (
    UpdateProductApiMapper,
)
from src.modules.products.presentation.api.schemas.update_product_schema import (
    UpdateProductRequestSchema,
    UpdateProductResponseSchema,
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
    path="/{product_id}",
    summary="Update a product by supplying its ID.",
    description=(
        "Update a product by supplying its ID. The request must include the "
        "optional values to be updated."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[UpdateProductResponseSchema],
            "description": "The product was updated successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid request data or business rule validation errors.",
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
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An unexpected error occurred.",
        },
    },
)
async def update_product(
    product_id: UUID,
    request: UpdateProductRequestSchema,
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Update a product by supplying its ID.

    This endpoint updates an existing product with the provided optional values.

    Args:
        product_id (UUID): The ID of the product to update.
        request (UpdateProductRequestSchema): The request schema containing the optional values to update.
        use_case (UpdateProductUseCase): The UpdateProductUseCase instance.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: A JSON response containing the updated product.
    """
    result: UpdatedProductResponseDto = await use_case.execute(
        command=UpdateProductApiMapper.to_command(request, product_id),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub,
            role=current_user.role,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Product updated successfully.",
                data=UpdateProductApiMapper.to_response(result),
            )
        ),
    )
