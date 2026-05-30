from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import (
    PlainPasswordVO,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestUpdateWarehouseRouter:
    @pytest.mark.asyncio
    async def test_should_update_warehouse_and_return_200_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier with a valid token and payload receives 200 with updated warehouse data."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        payload = {
            "name": faker.company(),
            "address": faker.address(),
        }

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json=payload,
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Warehouse updated successfully."
        assert body["data"]["id"] == warehouse_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["name"] == payload["name"]
        assert body["data"]["address"] == payload["address"]
        assert body["data"]["is_active"] is True
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_persist_updated_warehouse_data(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Updated warehouse data must persist and be returned by subsequent GET requests."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        updated_payload = {
            "name": faker.company(),
            "address": faker.address(),
        }

        update_response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json=updated_payload,
            headers=headers,
        )

        assert update_response.status_code == status.HTTP_200_OK

        get_response = await async_client.get(
            url="/api/v1/warehouses/",
            headers=headers,
        )

        warehouses = get_response.json()["data"]["warehouses"]

        updated_warehouse = next(
            warehouse for warehouse in warehouses if warehouse["id"] == warehouse_id
        )

        assert updated_warehouse["name"] == updated_payload["name"]
        assert updated_warehouse["address"] == updated_payload["address"]

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Requests without an Authorization header must be rejected with 401."""
        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}",
            json={
                "name": faker.company(),
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
        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}",
            json={
                "name": faker.company(),
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

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}",
            json={
                "name": faker.company(),
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

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}",
            json={
                "name": faker.company(),
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
        """A token with the ADMIN role must be rejected — only SUPPLIER may update warehouses."""
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

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}",
            json={
                "name": faker.company(),
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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": "  ",
                "address": faker.address(),
            },
            headers=headers,
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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": "AB",
                "address": faker.address(),
            },
            headers=headers,
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
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A name of 100 or more characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        long_name = "W" * 100

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": long_name,
                "address": faker.address(),
            },
            headers=headers,
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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": faker.company(),
                "address": "  ",
            },
            headers=headers,
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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": faker.company(),
                "address": "AB",
            },
            headers=headers,
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
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An address of 255 or more characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = create_response.json()["data"]["id"]

        long_address = "A" * 255

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}",
            json={
                "name": faker.company(),
                "address": long_address,
            },
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Invalid warehouse address."
        assert any("255 characters" in detail for detail in body["details"])
