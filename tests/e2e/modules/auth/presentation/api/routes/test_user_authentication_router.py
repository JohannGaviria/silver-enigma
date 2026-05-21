import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class TestUserAuthenticationRouter:
    @pytest.mark.asyncio
    async def test_should_return_tokens_when_credentials_are_valid(
        self,
        async_client: AsyncClient,
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the login endpoint returns access and refresh tokens.

        when the credentials are valid.
        """
        response = await async_client.post(
            url="api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": str(plain_password_valid),
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "User authentication successful."
        assert "token" in body["data"]["access"]
        assert "token_type" in body["data"]["access"]
        assert "expires_in" in body["data"]["access"]
        assert "token" in body["data"]["refresh"]
        assert "expires_in" in body["data"]["refresh"]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_email_is_invalid(
        self, async_client: AsyncClient, plain_password_valid: PlainPasswordVO
    ) -> None:
        """Test that the login endpoint returns a validation error.

        when the email format is invalid.
        """
        invalid_email = "invalid-email.com"

        response = await async_client.post(
            url="api/v1/auth/login",
            json={"email": invalid_email, "password": str(plain_password_valid)},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid email address provided."
        assert body["context"]["email"] == invalid_email
        assert "Email format is invalid." in body["details"]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_password_is_invalid(
        self, async_client: AsyncClient, created_user: UserEntity, faker: Faker
    ) -> None:
        """Test that the login endpoint returns a validation error.

        when the password format is invalid.
        """
        response = await async_client.post(
            url="api/v1/auth/login",
            json={
                "email": str(created_user.email),
                "password": faker.password(
                    length=5, special_chars=False, digits=False, lower_case=True
                ),
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid plain password provided."

        assert "Password must be at least 8 characters long." in body["details"]
        assert (
            "Password must contain at least one numeric character." in body["details"]
        )
        assert (
            "Password must contain at least one special character." in body["details"]
        )

    @pytest.mark.asyncio
    async def test_should_return_authentication_error_when_user_does_not_exist(
        self, async_client: AsyncClient, faker: Faker
    ) -> None:
        """Test that the login endpoint returns an authentication error.

        when the user does not exist.
        """
        response = await async_client.post(
            url="api/v1/auth/login",
            json={
                "email": faker.email(domain="example.com"),
                "password": faker.password(),
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication failed due to invalid credentials."

    @pytest.mark.asyncio
    async def test_should_return_authentication_error_when_password_is_incorrect(
        self, async_client: AsyncClient, created_user: UserEntity, faker: Faker
    ) -> None:
        """Test that the login endpoint returns an authentication error.

        when the password is incorrect.
        """
        response = await async_client.post(
            url="api/v1/auth/login",
            json={"email": str(created_user.email), "password": faker.password()},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication failed due to invalid credentials."

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_required_fields_are_missing(
        self, async_client: AsyncClient, faker: Faker
    ) -> None:
        """Test that the login endpoint returns a validation error.

        when required fields are missing.
        """
        response = await async_client.post(
            url="api/v1/auth/login", json={"email": faker.email()}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_request_body_is_invalid(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that the login endpoint returns a validation error.

        when the request body is invalid.
        """
        response = await async_client.post(url="api/v1/auth/login", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
