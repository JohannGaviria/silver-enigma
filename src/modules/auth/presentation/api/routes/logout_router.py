"""This module contains the logout router."""

from fastapi import APIRouter, Depends, status

from src.modules.auth.application.use_cases.logout_use_case import LogoutUseCase
from src.modules.auth.presentation.api.compositions.use_case_composition import (
    get_logout_use_case,
)
from src.modules.auth.presentation.api.mappers.logout_mapper import LogoutApiMapper
from src.modules.auth.presentation.api.schemas.logout_schema import LogoutRequestSchema
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO
from src.shared.presentation.api.compositions.security_composition import (
    get_current_user,
)
from src.shared.presentation.api.schemas.schema import ErrorsResponseSchema

router = APIRouter()


@router.post(
    path="/logout",
    summary="Logout a user",
    description="This endpoint logs out a user by deleting the refresh token from the cache.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "User successfully logged out."},
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorsResponseSchema,
            "description": "Invalid request body.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "Invalid or expired refresh token.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "Invalid request body.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "Internal server error.",
        },
    },
)
async def logout(
    request: LogoutRequestSchema,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
    current_user: AccessTokenPayloadVO = Depends(get_current_user),
) -> None:
    """Logout a user endpoint.

    This endpoint logs out a user by deleting the refresh token from the cache.

    Args:
        request (LogoutRequestSchema): The request schema containing the refresh token.
        use_case (LogoutUseCase): The use case for logging out a user.
        current_user (AccessTokenPayloadVO): The current user's access token payload.

    Returns:
        None
    """
    await use_case.execute(LogoutApiMapper.to_command(request))
