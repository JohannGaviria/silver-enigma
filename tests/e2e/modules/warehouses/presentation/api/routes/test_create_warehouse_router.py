from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestCreateWarehouseRouter:
    @pytest.mark.asyncio
    async def test_should_create_warehouse_and_return_201_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier with a valid token and valid payload receives 201 with warehouse data."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        payload = {
            "name": faker.name(),
            "address": faker.address(),
        }

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["status"] == "success"
        assert body["message"] == "Warehouse created successfully."
        assert body["data"]["name"] == payload["name"]
        assert body["data"]["address"] == payload["address"]
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is True
        assert body["data"]["id"] is not None
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_associate_warehouse_with_authenticated_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The supplier_id in the response must match the authenticated user's ID."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["data"]["supplier_id"] == str(created_supplier.id)

    @pytest.mark.asyncio
    async def test_should_set_is_active_true_on_newly_created_warehouse(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A freshly created warehouse must always be active."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["data"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Requests without an Authorization header must be rejected with 401."""
        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication credentials were not provided."

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_invalid(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """A malformed token string must be rejected with 401."""
        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": "Bearer this_is_not_a_valid_jwt"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert (
            body["message"] == "Authentication failed due to an invalid access token."
        )

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_has_expired(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """An expired token must be rejected with 401."""
        from src.config import settings

        expired_token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.SUPPLIER.value,
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Your session has expired. Please authenticate again."

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_not_a_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """A token with a non-SUPPLIER role must be rejected with 403."""
        from src.config import settings

        buyer_token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.BUYER.value,
                "exp": datetime.now(UTC) + timedelta(minutes=10),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_admin(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """A token with the ADMIN role must also be rejected — only SUPPLIER may create warehouses."""
        from src.config import settings

        admin_token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.ADMIN.value,
                "exp": datetime.now(UTC) + timedelta(minutes=10),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.name(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_name_is_empty(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An empty warehouse name must be rejected with 400 and validation details."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": "  ", "address": faker.address()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse name."
        assert body["context"]["name"] == "  "
        assert any("empty" in detail.lower() for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_name_is_too_short(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A name shorter than 3 characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": "AB", "address": faker.address()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse name."
        assert body["context"]["name"] == "AB"
        assert any("3 characters" in detail for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_name_is_too_long(
        self,
        async_client: AsyncClient,
        created_supplier: UserEntity,
        faker: Faker,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A name of 100 or more characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        long_name = "W" * 100

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": long_name, "address": faker.address()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse name."
        assert any("100 characters" in detail for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_address_is_empty(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An empty address must be rejected with 400 and validation details."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name(), "address": "  "},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse address."
        assert body["context"]["address"] == "  "
        assert any("empty" in detail.lower() for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_address_is_too_short(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An address shorter than 3 characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name(), "address": "AB"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse address."
        assert body["context"]["address"] == "AB"
        assert any("3 characters" in detail for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_warehouse_address_is_too_long(
        self,
        async_client: AsyncClient,
        created_supplier: UserEntity,
        faker: Faker,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An address of 255 or more characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        long_address = "A" * 255

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name(), "address": long_address},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse address."
        assert any("255 characters" in detail for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_422_when_name_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the name field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"address": faker.address()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_address_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the address field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_request_body_is_empty(
        self,
        async_client: AsyncClient,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An empty request body must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_allow_supplier_to_create_multiple_warehouses(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The same supplier can create several warehouses; each gets a unique ID."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        first = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name(), "address": faker.address()},
            headers=headers,
        )
        second = await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.name(), "address": faker.address()},
            headers=headers,
        )

        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_201_CREATED
        assert first.json()["data"]["id"] != second.json()["data"]["id"]
