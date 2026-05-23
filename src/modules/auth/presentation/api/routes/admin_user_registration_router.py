"""This module contains the admin user registration router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.application.dtos.admin_user_registration_dto import (
    AdminUserRegistrationResponseDto,
)
from src.modules.auth.application.use_cases.admin_user_registration_use_case import (
    AdminUserRegistrationUseCase,
)
from src.modules.auth.presentation.api.compositions.use_case_composition import (
    get_admin_user_registration_use_case,
)
from src.modules.auth.presentation.api.mappers.admin_user_registration_mapper import (
    AdminUserRegistrationMapper,
)
from src.modules.auth.presentation.api.schemas.admin_user_registration_schema import (
    AdminUserRegistrationRequestSchema,
    AdminUserRegistrationResponseSchema,
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
    path="/register",
    status_code=status.HTTP_201_CREATED,
    summary="New user registration by administrator.",
    description=(
        "Registers a new user with the system by an administrator."
        "The user is created with the provided details."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "model": SuccessResponseSchema[AdminUserRegistrationResponseSchema],
            "description": "User registration successful.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to invalid credentials.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to conflicting credentials.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to unexpected input.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to unauthorized access.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to insufficient permissions.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "User registration failed due to an internal error.",
        },
    },
)
async def admin_user_registration(
    request: AdminUserRegistrationRequestSchema,
    use_case: AdminUserRegistrationUseCase = Depends(
        get_admin_user_registration_use_case
    ),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> JSONResponse:
    """Register a new user by an administrator.

    This endpoint registers a new user with the system by an administrator.
    The user is created with the provided details.

    Args:
        request (AdminUserRegistrationRequestSchema): Parsed and validated request body.
        use_case (AdminUserRegistrationUseCase): Injected use case instance.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        JSONResponse: HTTP 201 with user registration response payload.
    """
    result: AdminUserRegistrationResponseDto = await use_case.execute(
        AdminUserRegistrationMapper.to_command(request, current_user.role)
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="User registration successful.",
                data=AdminUserRegistrationMapper.to_response(result),
            )
        ),
    )
