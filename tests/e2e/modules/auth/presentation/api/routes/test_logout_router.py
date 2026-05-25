"""E2E tests for the logout endpoint (POST /api/v1/auth/logout)."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.config import settings
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestLogoutRouter:
    @pytest.mark.asyncio
    async def test_should_logout_user_and_invalidate_refresh_token_when_request_is_valid(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the logout endpoint logs out the user, invalidates the refresh token.

        and returns an empty response when the request is valid.
        """
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        login_body = login_response.json()
        access_token = login_body["data"]["access"]["token"]
        refresh_token = login_body["data"]["refresh"]["token"]

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_refresh_token_is_used_after_logout(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the refresh endpoint returns an unauthorized error.

        when the refresh token is used after logout.
        """
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        login_body = login_response.json()
        access_token = login_body["data"]["access"]["token"]
        refresh_token = login_body["data"]["refresh"]["token"]

        logout_response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_response.status_code == status.HTTP_204_NO_CONTENT

        refresh_response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        refresh_body = refresh_response.json()

        assert refresh_response.status_code == status.HTTP_403_FORBIDDEN
        assert refresh_body["status"] == "error"
        assert refresh_body["message"] == "Session not found."

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the logout endpoint returns an unauthorized error.

        when the access token is missing.
        """
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication credentials were not provided."

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_access_token_is_invalid(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the logout endpoint returns an unauthorized error.

        when the access token is invalid.
        """
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": "Bearer invalid_token"},
        )
        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert (
            body["message"] == "Authentication failed due to an invalid access token."
        )

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_access_token_has_expired(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
    ) -> None:
        """Test that the logout endpoint returns an unauthorized error.

        when the access token has expired.
        """
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        expired_token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": str(created_user.id),
                "role": UserRoleEnum.ADMIN.value,
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Your session has expired. Please authenticate again."

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_refresh_token_is_invalid(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Test that the logout endpoint returns a validation error.

        when the refresh token is invalid (empty string).
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={"refresh_token": "   "},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert (
            body["message"] == "Authentication failed due to an invalid access token."
        )
        assert body["details"] == ["Token cannot be empty."]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_required_fields_are_missing(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Test that the logout endpoint returns a validation error.

        when required fields are missing.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/auth/logout",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
