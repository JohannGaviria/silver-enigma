"""This module contains the user authentication router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.application.dtos.user_authentication_dto import (
    UserAuthenticationResponse,
)
from src.modules.auth.application.use_cases.user_authentication_use_case import (
    UserAuthenticationUseCase,
)
from src.modules.auth.presentation.api.compositions.use_case_composition import (
    get_user_authentication_use_case,
)
from src.modules.auth.presentation.api.mappers.user_authentication_mapper import (
    UserAuthenticationMapper,
)
from src.modules.auth.presentation.api.schemas.user_authentication_schema import (
    UserAuthenticationRequest,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponse, SuccessResponse

router = APIRouter()


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description=(
        "Validates the user's credentials and, on success, returns a short-lived "
        "JWT access token together with an opaque refresh token stored in Redis."
    ),
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponse,
            "description": "User authentication successful.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponse,
            "description": "User authentication failed due to invalid credentials.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponse,
            "description": "User authentication failed due to unexpected input.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponse,
            "description": "User authentication failed due to unauthorized access.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponse,
            "description": "User authentication failed due to an internal error.",
        },
    },
)
async def user_authentication(
    request: UserAuthenticationRequest,
    use_case: UserAuthenticationUseCase = Depends(get_user_authentication_use_case),
) -> JSONResponse:
    """Authenticate a user and issue access + refresh tokens.

    This endpoint validates the user's credentials and, on success, returns a
    short-lived JWT access token together with an opaque refresh token stored
    in Redis.

    Args:
        request (UserAuthenticationRequest): Parsed and validated request body.
        use_case (UserAuthenticationUseCase): Injected use case instance.

    Returns:
        JSONResponse: HTTP 200 with access and refresh token payloads.
    """
    result: UserAuthenticationResponse = await use_case.execute(
        UserAuthenticationMapper.to_command(request)
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponse(
                message="User authentication successful.",
                data=UserAuthenticationMapper.to_response(result),
            )
        ),
    )
