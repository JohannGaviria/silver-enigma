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


class TestToggleProductStatusRouter:
    @pytest.mark.asyncio
    async def test_should_deactivate_product_and_return_200_when_request_is_valid(
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

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Product status toggled successfully."
        assert body["data"]["id"] == product_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_should_activate_product_and_return_200_when_request_is_valid(
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

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        deactivate_response = await async_client.patch(
            url=f"/api/v1/products/{product_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        assert deactivate_response.status_code == status.HTTP_200_OK

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}/status",
            json={"is_active": True},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Product status toggled successfully."
        assert body["data"]["id"] == product_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
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
        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
            json={"is_active": False},
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

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
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
            url=f"/api/v1/products/{faker.uuid4()}/status",
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
            url=f"/api/v1/products/{faker.uuid4()}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

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

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_403_when_supplier_attempts_to_toggle_product_owned_by_another_supplier(
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

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        product_id = create_response.json()["data"]["id"]

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
            url=f"/api/v1/products/{product_id}/status",
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
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
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
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}/status",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_409_when_product_has_active_orders(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
        created_product_with_active_orders: None,
    ) -> None:
        """Products with active orders cannot have their status toggled."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}/status",
            json={"is_active": False},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_409_CONFLICT
        assert body["status"] == "error"
