"""This module contains the get product stock router."""

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.products.application.dtos.get_product_catalog_dto import (
    GetProductCatalogResponseDto,
)
from src.modules.products.application.use_cases.get_product_catalog_use_case import (
    GetProductCatalogUseCase,
)
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.presentation.api.compositions.use_case_composition import (
    get_get_product_catalog_use_case,
)
from src.modules.products.presentation.api.mappers.get_product_catalog_mapper import (
    GetProductCatalogApiMapper,
)
from src.modules.products.presentation.api.schemas.get_product_catalog_schema import (
    GetProductCatalogResponseSchema,
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
    summary="Retrieve product catalog.",
    description="Retrieves a paginated list of products and their stock information.",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[GetProductCatalogResponseSchema],
            "description": "Product catalog retrieved successfully.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": (
                "Invalid request parameters."
                "This may occur when the pagination parameters are outside the allowed range."
            ),
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Authentication credentials were not provided or are invalid.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": (
                "The authenticated user does not have permission to access "
                "the requested product catalog information."
            ),
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "The request payload is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An unexpected error occurred while retrieving the product catalog.",
        },
    },
)
async def get_product_catalog(
    name: str | None = Query(
        default=None, description="Name of the product to filter by."
    ),
    unit_of_measure: UnitOfMeasureEnum | None = Query(
        default=None, description="Unit of measure of the product to filter by."
    ),
    page: int = Query(default=1, ge=1, description="Page number to retrieve."),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of stock records returned per page.",
    ),
    use_case: GetProductCatalogUseCase = Depends(get_get_product_catalog_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Get product catalog endpoint.

    Retrieves a paginated list of products and their stock information.
    The response includes product details such as name, description, unit of measure,
    unit price, and stock availability.

    Args:
        name (str | None, optional): Name of the product to filter by. Defaults to None.
        unit_of_measure (str | None, optional): Unit of measure of the product to filter by. Defaults to None.
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of records returned per page. Defaults to 10.
        use_case (GetProductCatalogUseCase): Application use case responsible for retrieving product catalog data.
        current_user (AccessTokenPayloadVO): Authenticated user requesting the information.

    Returns:
        JSONResponse: A successful response containing the paginated product catalog.
    """
    result: GetProductCatalogResponseDto = await use_case.execute(
        command=GetProductCatalogApiMapper.to_command(
            name=name,
            unit_of_measure=unit_of_measure,
            page=page,
            page_size=page_size,
        ),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Product catalog retrieved successfully.",
                data=GetProductCatalogApiMapper.to_response(result),
            )
        ),
    )
