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


class TestToggleWarehouseStatusRouter:
    @pytest.mark.asyncio
    async def test_should_deactivate_warehouse_and_return_200_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier can deactivate an active warehouse and receive the updated warehouse."""
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
            url=f"/api/v1/warehouses/{warehouse_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Warehouse status toggled successfully."
        assert body["data"]["id"] == warehouse_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_should_activate_warehouse_and_return_200_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier can activate an inactive warehouse and receive the updated warehouse."""
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

        deactivate_response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        assert deactivate_response.status_code == status.HTTP_200_OK

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}/status",
            json={"is_active": True},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Warehouse status toggled successfully."
        assert body["data"]["id"] == warehouse_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_should_persist_toggled_status(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The toggled warehouse status must persist and be visible through subsequent GET requests."""
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

        toggle_response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        assert toggle_response.status_code == status.HTTP_200_OK

        get_response = await async_client.get(
            url="/api/v1/warehouses/",
            headers=headers,
        )

        warehouses = get_response.json()["data"]["warehouses"]

        warehouse = next(
            warehouse for warehouse in warehouses if warehouse["id"] == warehouse_id
        )

        assert warehouse["is_active"] is False

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Requests without an Authorization header must be rejected with 401."""
        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
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
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
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
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
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
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
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
        """A token with the ADMIN role must be rejected — only SUPPLIER may toggle warehouse status."""
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
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_404_when_warehouse_does_not_exist(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Toggling a non-existent warehouse must return 404."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_403_when_supplier_attempts_to_toggle_warehouse_owned_by_another_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier cannot toggle a warehouse owned by another supplier."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        create_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        warehouse_id = create_response.json()["data"]["id"]

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

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{warehouse_id}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {other_supplier_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_422_when_is_active_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the is_active field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_request_body_is_empty(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An empty request body must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/warehouses/{faker.uuid4()}/status",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
