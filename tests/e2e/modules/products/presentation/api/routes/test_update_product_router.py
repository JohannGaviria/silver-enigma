from collections.abc import Awaitable, Callable
from decimal import Decimal

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)


class TestUpdateProductRouter:
    @pytest.mark.asyncio
    async def test_should_update_product_and_return_200_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier with a valid token and payload receives 200 with updated product data."""
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

        payload = {
            "name": faker.company(),
            "description": faker.text(max_nb_chars=100),
            "unit_of_measure": UnitOfMeasureEnum.KG.value,
            "unit_price": "25.75",
        }

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}",
            json=payload,
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["status"] == "success"
        assert body["message"] == "Product updated successfully."

        assert body["data"]["id"] == product_id
        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["name"] == payload["name"]
        assert body["data"]["description"] == payload["description"]
        assert body["data"]["unit_of_measure"] == payload["unit_of_measure"]
        assert Decimal(body["data"]["unit_price"]) == Decimal(payload["unit_price"])

        assert body["data"]["is_active"] is True
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_allow_partial_update_of_product(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Only supplied fields should be updated."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": "Original Product",
                "description": "Original Description",
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product = create_response.json()["data"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product['id']}",
            json={
                "name": "Updated Product",
            },
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK

        assert body["data"]["name"] == "Updated Product"
        assert body["data"]["description"] == product["description"]
        assert body["data"]["unit_of_measure"] == product["unit_of_measure"]
        assert Decimal(body["data"]["unit_price"]) == Decimal(product["unit_price"])

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
    ) -> None:
        """Requests without an Authorization header must be rejected with 401."""
        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}",
            json={"name": faker.company()},
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
            url=f"/api/v1/products/{faker.uuid4()}",
            json={"name": faker.company()},
            headers={"Authorization": "Bearer invalid_token"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"
        assert (
            body["message"] == "Authentication failed due to an invalid access token."
        )

    @pytest.mark.asyncio
    async def test_should_return_400_when_product_name_is_empty(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An empty product name must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}",
            json={"name": "  "},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Product name is invalid."
        assert body["context"]["name"] == "  "

    @pytest.mark.asyncio
    async def test_should_return_400_when_product_name_is_too_short(
        self,
        async_client: AsyncClient,
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
            url="/api/v1/products/",
            json={
                "name": "Original Product",
                "description": "Description",
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}",
            json={"name": "AB"},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["message"] == "Product name is invalid."

    @pytest.mark.asyncio
    async def test_should_return_400_when_unit_price_is_negative(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A negative unit price must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.company(),
                "description": faker.text(),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        product_id = create_response.json()["data"]["id"]

        response = await async_client.patch(
            url=f"/api/v1/products/{product_id}",
            json={"unit_price": "-1.00"},
            headers=headers,
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Unit price is invalid."

    @pytest.mark.asyncio
    async def test_should_return_422_when_unit_of_measure_is_invalid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An invalid unit_of_measure must fail schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}",
            json={
                "unit_of_measure": "INVALID",
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_404_when_product_does_not_exist(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Updating a non-existing product must return 404."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.patch(
            url=f"/api/v1/products/{faker.uuid4()}",
            json={"name": faker.company()},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
