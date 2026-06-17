"""This module contains the create order API routes."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.orders.application.dtos.create_order_dto import CreateOrderResponseDto
from src.modules.orders.application.use_cases.create_order_use_case import (
    CreateOrderUseCase,
)
from src.modules.orders.presentation.api.compositions.use_case_composition import (
    get_create_order_use_case,
)
from src.modules.orders.presentation.api.mappers.create_order_mapper import (
    CreateOrderApiMapper,
)
from src.modules.orders.presentation.api.schemas.create_order_schema import (
    CreateOrderRequestSchema,
    CreateOrderResponseSchema,
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
    summary="Create a new order",
    description=(
        "Creates a new order for the authenticated user. "
        "The request validates the provided products and quantities, "
        "applies the order creation business rules, and persists the order "
        "with its associated items."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[CreateOrderResponseSchema],
            "description": "Order successfully created.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": (
                "The request contains invalid data or violates order "
                "creation business rules."
            ),
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": (
                "Authentication failed or the access token is missing, "
                "invalid, or expired."
            ),
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": (
                "The authenticated user does not have permission to create an order."
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorsResponseSchema,
            "description": (
                "One or more required resources were not found, such as "
                "referenced products or related entities."
            ),
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ErrorsResponseSchema,
            "description": (
                "The request body contains validation errors and could not "
                "be processed."
            ),
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": (
                "An unexpected server error occurred while creating the order."
            ),
        },
    },
)
async def create_order(
    request: CreateOrderRequestSchema,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Creates a new order for the authenticated user.

    The endpoint receives an order creation request containing the required
    order items. The use case validates the request, applies domain rules,
    creates the order entity, and stores it through the configured persistence
    layer.

    Args:
        request (CreateOrderRequestSchema):
            Data required to create the order, including the products and
            requested quantities.

        use_case (CreateOrderUseCase):
            Application service responsible for executing the order creation
            workflow.

        current_user (AccessTokenPayloadVO):
            Authenticated user information extracted from the access token.

    Returns:
        JSONResponse:
            A successful response containing the created order information.

    Raises:
        HTTPException:
            When authentication, authorization, validation, business rules,
            resource lookup, or persistence operations fail.
    """
    result: CreateOrderResponseDto = await use_case.execute(
        command=CreateOrderApiMapper.to_command(request),
        authenticated_user=AuthenticatedUserApiMapper.to_command(
            user_id=current_user.sub, role=current_user.role
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Order created successfully.",
                data=CreateOrderApiMapper.to_response(result),
            )
        ),
    )
