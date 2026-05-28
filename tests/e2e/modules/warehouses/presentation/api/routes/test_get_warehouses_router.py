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


class TestGetWarehousesRouter:
    @pytest.mark.asyncio
    async def test_should_return_200_with_empty_list_when_supplier_has_no_warehouses(
        self,
        async_client: AsyncClient,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier with no warehouses receives 200 with an empty list."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Successfully retrieved warehouses."
        assert body["data"]["warehouses"] == []

    @pytest.mark.asyncio
    async def test_should_return_200_with_warehouses_after_creating_them(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier who has created warehouses should see them listed in the response."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        for _ in range(2):
            await async_client.post(
                url="/api/v1/warehouses/",
                json={"name": faker.company(), "address": faker.address()},
                headers=headers,
            )

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert len(body["data"]["warehouses"]) == 2

    @pytest.mark.asyncio
    async def test_should_return_correct_warehouse_fields(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Each warehouse item in the response must expose all expected fields."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {"name": faker.company(), "address": faker.address()}
        await async_client.post(
            url="/api/v1/warehouses/",
            json=payload,
            headers=headers,
        )

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers=headers,
        )

        body = response.json()
        warehouse = body["data"]["warehouses"][0]

        assert response.status_code == status.HTTP_200_OK
        assert warehouse["id"] is not None
        assert warehouse["supplier_id"] == str(created_supplier.id)
        assert warehouse["name"] == payload["name"]
        assert warehouse["address"] == payload["address"]
        assert warehouse["is_active"] is True
        assert warehouse["created_at"] is not None
        assert warehouse["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_only_return_warehouses_belonging_to_authenticated_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Warehouses from other suppliers must not appear in the response."""
        token_a = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.company(), "address": faker.address()},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        from src.config import settings

        other_supplier_token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.SUPPLIER.value,
                "exp": datetime.now(UTC) + timedelta(minutes=10),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers={"Authorization": f"Bearer {other_supplier_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["data"]["warehouses"] == []

    @pytest.mark.asyncio
    async def test_should_return_all_warehouses_created_by_the_same_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Every warehouse created by a supplier must appear in the list."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        names = [faker.company() for _ in range(3)]
        for name in names:
            await async_client.post(
                url="/api/v1/warehouses/",
                json={"name": name, "address": faker.address()},
                headers=headers,
            )

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers=headers,
        )

        body = response.json()
        returned_names = {w["name"] for w in body["data"]["warehouses"]}

        assert response.status_code == status.HTTP_200_OK
        assert set(names) == returned_names

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Requests without an Authorization header must be rejected with 401."""
        response = await async_client.get(url="/api/v1/warehouses/")

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Authentication credentials were not provided."

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_invalid(
        self,
        async_client: AsyncClient,
    ) -> None:
        """A malformed token string must be rejected with 401."""
        response = await async_client.get(
            url="/api/v1/warehouses/",
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

        response = await async_client.get(
            url="/api/v1/warehouses/",
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

        response = await async_client.get(
            url="/api/v1/warehouses/",
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
        """A token with the ADMIN role must be rejected — only SUPPLIER may list warehouses."""
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

        response = await async_client.get(
            url="/api/v1/warehouses/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_same_warehouses_on_second_request_from_cache(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Two consecutive GET requests for the same supplier must return identical data."""
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.company(), "address": faker.address()},
            headers=headers,
        )

        first = await async_client.get(url="/api/v1/warehouses/", headers=headers)
        second = await async_client.get(url="/api/v1/warehouses/", headers=headers)

        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_200_OK
        assert first.json()["data"] == second.json()["data"]

    @pytest.mark.asyncio
    async def test_should_reflect_new_warehouse_after_cache_invalidation(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """After creating a new warehouse the GET endpoint must return the updated list.

        The create endpoint invalidates the cache, so the next GET should re-query
        the database and return all warehouses including the newly created one.
        """
        access_token = await access_token_factory(
            str(created_supplier.email), str(plain_password_valid)
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": faker.company(), "address": faker.address()},
            headers=headers,
        )
        first_get = await async_client.get(url="/api/v1/warehouses/", headers=headers)
        assert len(first_get.json()["data"]["warehouses"]) == 1

        second_name = faker.company()
        await async_client.post(
            url="/api/v1/warehouses/",
            json={"name": second_name, "address": faker.address()},
            headers=headers,
        )

        second_get = await async_client.get(url="/api/v1/warehouses/", headers=headers)
        returned_names = {w["name"] for w in second_get.json()["data"]["warehouses"]}

        assert len(second_get.json()["data"]["warehouses"]) == 2
        assert second_name in returned_names
