import secrets
from collections.abc import Awaitable, Callable

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestReissueSessionCredentialsRouter:
    @pytest.mark.asyncio
    async def test_should_return_new_tokens_when_refresh_token_is_valid(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Reissuing with a valid refresh token returns new access and refresh tokens."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        assert login_response.status_code == status.HTTP_200_OK
        login_body = login_response.json()
        refresh_token = login_body["data"]["refresh"]["token"]

        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Successfully reissued session credentials."

        access = body["data"]["access"]
        assert "token" in access
        assert access["token_type"] == "Bearer"
        assert isinstance(access["expires_in"], int)
        assert access["expires_in"] > 0

        refresh = body["data"]["refresh"]
        assert "token" in refresh
        assert isinstance(refresh["expires_in"], int)
        assert refresh["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_should_return_different_tokens_after_reissue(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """The newly issued tokens must differ from the originals."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        login_body = login_response.json()
        original_access_token = login_body["data"]["access"]["token"]
        original_refresh_token = login_body["data"]["refresh"]["token"]

        reissue_response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": original_refresh_token},
        )

        reissue_body = reissue_response.json()
        new_access_token = reissue_body["data"]["access"]["token"]
        new_refresh_token = reissue_body["data"]["refresh"]["token"]

        assert new_access_token != original_access_token
        assert new_refresh_token != original_refresh_token

    @pytest.mark.asyncio
    async def test_should_invalidate_refresh_token_after_use(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """A refresh token must be invalidated (one-time use) after being consumed."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        first_response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert first_response.status_code == status.HTTP_200_OK

        second_response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        second_body = second_response.json()

        assert second_response.status_code == status.HTTP_403_FORBIDDEN
        assert second_body["status"] == "error"
        assert second_body["message"] == "Session not found."

    @pytest.mark.asyncio
    async def test_should_return_forbidden_when_refresh_token_does_not_exist_in_cache(
        self,
        async_client: AsyncClient,
    ) -> None:
        """An arbitrary string that was never stored in cache must be rejected."""
        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": "this-token-was-never-stored-in-cache"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"
        assert body["message"] == "Session not found."

    @pytest.mark.asyncio
    async def test_should_return_forbidden_when_refresh_token_is_random_string(
        self,
        async_client: AsyncClient,
    ) -> None:
        """A random token string that is not in cache must return 403."""
        random_token = secrets.token_urlsafe(64)

        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": random_token},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"
        assert body["message"] == "Session not found."

    @pytest.mark.asyncio
    async def test_should_return_unprocessable_entity_when_refresh_token_field_is_missing(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Omitting the refresh_token field entirely must fail schema validation."""
        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_unprocessable_entity_when_request_body_is_not_json(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Sending a non-JSON body must fail schema validation."""
        response = await async_client.post(
            url="/api/v1/auth/refresh",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_unprocessable_entity_when_refresh_token_is_null(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Sending null as the refresh_token value must fail schema validation."""
        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": None},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_allow_chained_reissue_using_newly_issued_refresh_token(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """The new refresh token returned by a reissue must itself be usable."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        first_refresh_token = login_response.json()["data"]["refresh"]["token"]

        first_reissue = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": first_refresh_token},
        )
        assert first_reissue.status_code == status.HTTP_200_OK
        second_refresh_token = first_reissue.json()["data"]["refresh"]["token"]

        second_reissue = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": second_refresh_token},
        )
        second_body = second_reissue.json()

        assert second_reissue.status_code == status.HTTP_200_OK
        assert second_body["status"] == "success"
        assert "token" in second_body["data"]["access"]
        assert "token" in second_body["data"]["refresh"]

    @pytest.mark.asyncio
    async def test_should_return_bearer_token_type_in_access_token(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """The access token in the reissue response must always be of type Bearer."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["data"]["access"]["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_should_return_access_token_that_can_authenticate_subsequent_requests(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The access token returned by reissue must be accepted by protected endpoints."""
        login_response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )
        refresh_token = login_response.json()["data"]["refresh"]["token"]

        reissue_response = await async_client.post(
            url="/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        new_access_token = reissue_response.json()["data"]["access"]["token"]

        faker = Faker()
        protected_response = await async_client.post(
            url="/api/v1/auth/register",
            json={
                "name": faker.name(),
                "email": faker.email(),
                "password": faker.password(),
                "role": UserRoleEnum.BUYER,
            },
            headers={"Authorization": f"Bearer {new_access_token}"},
        )

        assert protected_response.status_code != status.HTTP_401_UNAUTHORIZED
