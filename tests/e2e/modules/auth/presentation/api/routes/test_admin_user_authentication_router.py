from collections.abc import Awaitable, Callable

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestAdminUserRegistrationRouter:
    @pytest.mark.asyncio
    async def test_should_register_user_and_return_created_user_data_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the register endpoint creates and persists a new user and returns.

        the created user data when the request is valid
        and the current user is an administrator.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["status"] == "success"
        assert body["message"] == "User registration successful."
        assert body["data"]["name"] == payload["name"]
        assert body["data"]["email"] == payload["email"]
        assert body["data"]["role"] == payload["role"]
        assert body["data"]["id"] is not None
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_return_conflict_error_when_user_already_exists(
        self,
        async_client: AsyncClient,
        faker: Faker,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
    ) -> None:
        """Test that the register endpoint returns a conflict error.

        when the user already exists.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_409_CONFLICT
        assert body["status"] == "error"
        assert body["message"] == "A user with the same email already exists."
        assert body["details"] == ["The user already exists."]

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns an unauthorized error.

        when the access token is missing.
        """
        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication credentials were not provided."

    @pytest.mark.asyncio
    async def test_should_return_unauthorized_error_when_access_token_is_invalid(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns an unauthorized error.

        when the access token is invalid.
        """
        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
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
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns an unauthorized error.

        when the access token has expired.
        """
        from datetime import UTC, datetime, timedelta

        from src.config import settings

        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.ADMIN.value,
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Your session has expired. Please authenticate again."

    @pytest.mark.asyncio
    async def test_should_return_forbidden_error_when_user_has_insufficient_permissions(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a forbidden error.

        when the current user has insufficient permissions.
        """
        from datetime import UTC, datetime, timedelta

        from src.config import settings

        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.BUYER.value,
                "exp": datetime.now(UTC) + timedelta(minutes=10),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"
        assert body["message"] == "Insufficient permissions."

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_name_is_invalid(
        self,
        async_client: AsyncClient,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a validation error.

        when the name is invalid.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": "john",
            "email": faker.email(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid name provided."
        assert body["context"] == {
            "name": "john",
        }
        assert body["details"] == [
            "Name must include at least first name and last name",
        ]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_email_is_invalid(
        self,
        async_client: AsyncClient,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a validation error.

        when the email format is invalid.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "email": "invalid-email.com",
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid email address provided."
        assert body["context"] == {
            "email": "invalid-email.com",
        }
        assert body["details"] == [
            "Email format is invalid.",
        ]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_password_is_invalid(
        self,
        async_client: AsyncClient,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: str,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a validation error.

        when the password format is invalid.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(
                length=5, special_chars=False, digits=False, lower_case=True
            ),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid plain password provided."
        assert body["details"] == [
            "Password must be at least 8 characters long.",
            "Password must contain at least one numeric character.",
            "Password must contain at least one special character.",
        ]

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_role_is_invalid(
        self,
        async_client: AsyncClient,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a validation error.

        when the role is invalid.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "password": faker.password(),
            "role": "invalid_role",
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_validation_error_when_required_fields_are_missing(
        self,
        async_client: AsyncClient,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_user: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
    ) -> None:
        """Test that the register endpoint returns a validation error.

        when required fields are missing.
        """
        access_token = await access_token_factory(
            str(created_user.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "password": faker.password(),
            "role": UserRoleEnum.BUYER,
        }

        response = await async_client.post(
            url="api/v1/auth/register",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
