"""This module contains the reissue session credentials router."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.modules.auth.application.dtos.reissue_session_credentials_dto import (
    ReissueSessionCredentialsResponseDto,
)
from src.modules.auth.application.use_cases.reissue_session_credentials_use_case import (
    ReissueSessionCredentialsUseCase,
)
from src.modules.auth.presentation.api.compositions.use_case_composition import (
    get_reissue_session_credentials_use_case,
)
from src.modules.auth.presentation.api.mappers.reissue_session_credentials_mapper import (
    ReissueSessionCredentialsApiMapper,
)
from src.modules.auth.presentation.api.schemas.reissue_session_credentials_schema import (
    ReissueSessionCredentialsRequestSchema,
    ReissueSessionCredentialsResponseSchema,
)
from src.shared.presentation.api.schemas.schema import (
    ErrorsResponseSchema,
    SuccessResponseSchema,
)

router = APIRouter()


@router.post(
    path="/refresh",
    summary="Reissue session credentials.",
    description="Reissue session credentials for the user associated with the refresh token.",
    responses={
        status.HTTP_200_OK: {
            "model": SuccessResponseSchema[ReissueSessionCredentialsResponseSchema],
            "message": "Successfully reissued session credentials.",
            "description": "The response contains the reissued session credentials.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorsResponseSchema,
            "description": "The refresh token is invalid or has expired.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorsResponseSchema,
            "description": "The refresh token is invalid.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorsResponseSchema,
            "description": "An error occurred while processing the request.",
        },
    },
)
async def reissue_session_credentials(
    request: ReissueSessionCredentialsRequestSchema,
    use_case: ReissueSessionCredentialsUseCase = Depends(
        get_reissue_session_credentials_use_case
    ),
) -> JSONResponse:
    """Reissue session credentials endpoint.

    This endpoint is responsible for reissuing session credentials
    for the user associated with the refresh token.

    Args:
        request (ReissueSessionCredentialsRequestSchema): The request schema
            containing the refresh token.
        use_case (ReissueSessionCredentialsUseCase): The use case instance.

    Returns:
        JSONResponse: A JSON response containing the reissued session credentials.
    """
    result: ReissueSessionCredentialsResponseDto = await use_case.execute(
        ReissueSessionCredentialsApiMapper.to_command(request)
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(
            SuccessResponseSchema(
                message="Successfully reissued session credentials.",
                data=ReissueSessionCredentialsApiMapper.to_response(result),
            )
        ),
    )
