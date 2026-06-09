from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestGetWarehouseStockRouter:
    @pytest.mark.asyncio
    async def test_should_return_200_with_empty_inventory_when_warehouse_has_no_stock(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        warehouse_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = warehouse_response.json()["data"]["id"]

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{warehouse_id}/stock",
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"

    @pytest.mark.asyncio
    async def test_should_return_200_with_stock_inventory(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        warehouse_response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = warehouse_response.json()["data"]["id"]

        product_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = product_response.json()["data"]["id"]

        await async_client.post(
            url="/api/v1/inventory/movements",
            json={
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "quantity": 100,
            },
            headers=headers,
        )

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{warehouse_id}/stock",
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"

    @pytest.mark.asyncio
    async def test_should_return_paginated_inventory(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        warehouse_response = await async_client.post(
            "/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        warehouse_id = warehouse_response.json()["data"]["id"]

        for _ in range(15):
            product_response = await async_client.post(
                "/api/v1/products/",
                json={
                    "name": faker.company(),
                    "description": faker.text(max_nb_chars=100),
                    "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                    "unit_price": "10.50",
                },
                headers=headers,
            )

            await async_client.post(
                "/api/v1/inventory/movements",
                json={
                    "product_id": product_response.json()["data"]["id"],
                    "warehouse_id": warehouse_id,
                    "quantity": 10,
                },
                headers=headers,
            )

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{warehouse_id}/stock?page=1&page_size=10",
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
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
        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
            headers={"Authorization": "Bearer invalid_token"},
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
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Your session has expired. Please authenticate again."

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_buyer(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
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

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_admin(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        from src.config import settings

        token = jwt.encode(
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
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_should_return_200_when_warehouse_does_not_exist(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["data"]["warehouse_stock"] == []

    @pytest.mark.asyncio
    async def test_should_return_422_when_page_is_less_than_one(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock?page=0",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_page_size_exceeds_limit(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.get(
            url=f"/api/v1/products/warehouses/{faker.uuid4()}/stock?page_size=101",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
