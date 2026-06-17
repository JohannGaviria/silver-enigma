from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestCreateOrderRouter:
    @pytest.mark.asyncio
    async def test_should_create_order_and_return_201_when_request_is_valid(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        created_product: ProductEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A buyer with a valid token and valid items receives 201 with order data."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        payload = {
            "items": [
                {
                    "product_id": str(created_product.id),
                    "quantity": 2,
                }
            ]
        }

        response = await async_client.post(
            url="/api/v1/orders/",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED

        assert body["status"] == "success"
        assert body["message"] == "Order created successfully."

        assert body["data"]["buyer_id"] == str(created_buyer.id)

        assert body["data"]["id"] is not None
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

        assert body["data"]["status"] == "DRAFT"

        assert len(body["data"]["items"]) == 1

        item = body["data"]["items"][0]

        assert item["product_id"] == str(created_product.id)
        assert item["quantity"] == 2
        assert item["name"] == str(created_product.name)
        assert Decimal(item["unit_price"]) == created_product.unit_price.value()

    @pytest.mark.asyncio
    async def test_should_associate_order_with_authenticated_buyer(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        created_product: ProductEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The order buyer_id must match the authenticated user."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(created_product.id),
                        "quantity": 1,
                    }
                ]
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["data"]["buyer_id"] == str(created_buyer.id)

    @pytest.mark.asyncio
    async def test_should_create_order_with_multiple_items(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        created_products: list[ProductEntity],
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A buyer can create an order containing multiple products."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        payload = {
            "items": [
                {
                    "product_id": str(product.id),
                    "quantity": index + 1,
                }
                for index, product in enumerate(created_products)
            ]
        }

        response = await async_client.post(
            url="/api/v1/orders/",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert len(body["data"]["items"]) == len(created_products)

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_missing(
        self,
        async_client: AsyncClient,
        created_product: ProductEntity,
    ) -> None:
        """Requests without authorization must be rejected."""
        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(created_product.id),
                        "quantity": 1,
                    }
                ]
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_is_invalid(
        self,
        async_client: AsyncClient,
        created_product: ProductEntity,
    ) -> None:
        """Malformed JWT tokens must be rejected."""
        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(created_product.id),
                        "quantity": 1,
                    }
                ]
            },
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["status"] == "error"

    @pytest.mark.asyncio
    async def test_should_return_401_when_access_token_has_expired(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_product: ProductEntity,
    ) -> None:
        """Expired JWT tokens must be rejected."""
        from src.config import settings

        token = jwt.encode(
            {
                "jti": faker.uuid4(),
                "sub": faker.uuid4(),
                "role": UserRoleEnum.BUYER.value,
                "exp": datetime.now(UTC) - timedelta(minutes=5),
            },
            settings.TOKEN_SECRET_KEY,
            algorithm=settings.TOKEN_ALGORITHM,
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(created_product.id),
                        "quantity": 1,
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_should_return_422_when_items_field_is_missing(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Missing items must fail request validation."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_product_id_is_missing(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An item without product_id must fail validation."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "quantity": 1,
                    }
                ]
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_quantity_is_missing(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        created_product: ProductEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An item without quantity must fail validation."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(created_product.id),
                    }
                ]
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_400_when_product_does_not_exist(
        self,
        async_client: AsyncClient,
        created_buyer: UserEntity,
        plain_password_valid: PlainPasswordVO,
        faker: Faker,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Unknown referenced products must return not found."""
        access_token = await access_token_factory(
            str(created_buyer.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/orders/",
            json={
                "items": [
                    {
                        "product_id": str(faker.uuid4()),
                        "quantity": 1,
                    }
                ]
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
