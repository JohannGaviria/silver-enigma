"""This module contains the create product router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.create_product_dto import (
    CreateProductResponseDto,
)
from src.modules.products.application.use_cases.create_product_use_case import (
    CreateProductUseCase,
)
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_create_product_use_case,
)
from src.modules.products.presentation.api.mappers.create_product_mapper import (
    CreateProductApiMapper,
)
from src.modules.products.presentation.api.schemas.create_product_schema import (
    CreateProductRequestSchema,
    CreateProductResponseSchema,
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


@router.post(
    path="/",
    summary="Create a product for the supplier.",
    description="Creates a new product for the supplier.",
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[CreateProductResponseSchema],
            "description": "Product created successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Product creation failed due to invalid input.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Product creation failed due to invalid authentication.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "Product creation failed due to insufficient permissions.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Product creation failed due to an internal server error.",
        },
    },
)
async def create_product(
    request: CreateProductRequestSchema,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Create a product for the supplier.

    This endpoint creates a new product for the supplier and returns the created product.

    Args:
        request (CreateProductRequestSchema): The request schema for the create product endpoint.
        use_case (CreateProductUseCase): The CreateProductUseCase instance.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: A JSON response containing the created product.
    """
    response: CreateProductResponseDto = await use_case.execute(
        command=CreateProductApiMapper.to_command(request),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub,
            role=current_user.role,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Product created successfully.",
                data=CreateProductApiMapper.to_response(response),
            )
        ),
    )
