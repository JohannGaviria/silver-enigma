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


class TestAdjustStockRouter:
    async def _create_product(
        self,
        async_client: AsyncClient,
        faker: Faker,
        headers: dict[str, str],
    ) -> str:
        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        return response.json()["data"]["id"]

    async def _create_warehouse(
        self,
        async_client: AsyncClient,
        faker: Faker,
        headers: dict[str, str],
    ) -> str:
        response = await async_client.post(
            url="/api/v1/warehouses/",
            json={
                "name": faker.company(),
                "address": faker.address(),
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        return response.json()["data"]["id"]

    @pytest.mark.asyncio
    async def test_should_create_stock_and_return_200_when_stock_does_not_exist(
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

        product_id = await self._create_product(
            async_client,
            faker,
            headers,
        )

        warehouse_id = await self._create_warehouse(
            async_client,
            faker,
            headers,
        )

        response = await async_client.put(
            url=f"/api/v1/products/{product_id}/warehouses/{warehouse_id}/stock",
            json={"quantity": 100},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Stock adjusted successfully."

        assert body["data"]["product_id"] == product_id
        assert body["data"]["warehouse_id"] == warehouse_id
        assert body["data"]["total_stock"] == 100
        assert body["data"]["reserved_stock"] == 0
        assert body["data"]["stock_disponible"] == 100

        assert body["data"]["id"] is not None
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_update_existing_stock_and_return_200(
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

        product_id = await self._create_product(async_client, faker, headers)
        warehouse_id = await self._create_warehouse(async_client, faker, headers)

        first = await async_client.put(
            url=f"/api/v1/products/{product_id}/warehouses/{warehouse_id}/stock",
            json={"quantity": 100},
            headers=headers,
        )

        assert first.status_code == status.HTTP_200_OK

        response = await async_client.put(
            url=f"/api/v1/products/{product_id}/warehouses/{warehouse_id}/stock",
            json={"quantity": 250},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["data"]["total_stock"] == 250
        assert body["data"]["reserved_stock"] == 0

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
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
        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert body["message"] == "Your session has expired. Please authenticate again."

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_not_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_should_return_403_when_authenticated_user_is_admin(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_should_return_404_when_product_does_not_exist(
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

        warehouse_id = await self._create_warehouse(
            async_client,
            faker,
            headers,
        )

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{warehouse_id}/stock",
            json={"quantity": 100},
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_should_return_404_when_warehouse_does_not_exist(
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

        product_id = await self._create_product(
            async_client,
            faker,
            headers,
        )

        response = await async_client.put(
            url=f"/api/v1/products/{product_id}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": 100},
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_should_return_403_when_product_belongs_to_another_supplier(
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

        product_id = await self._create_product(async_client, faker, headers)
        warehouse_id = await self._create_warehouse(async_client, faker, headers)

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

        response = await async_client.put(
            url=f"/api/v1/products/{product_id}/warehouses/{warehouse_id}/stock",
            json={"quantity": 100},
            headers={"Authorization": f"Bearer {other_supplier_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_should_return_422_when_quantity_is_missing(
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={},
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_quantity_is_not_integer(
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": "abc"},
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_400_when_quantity_is_negative(
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={"quantity": -1},
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_should_return_422_when_request_body_is_empty(
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

        response = await async_client.put(
            url=f"/api/v1/products/{faker.uuid4()}/warehouses/{faker.uuid4()}/stock",
            json={},
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
