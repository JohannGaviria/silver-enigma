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
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestCreateProductRouter:
    @pytest.mark.asyncio
    async def test_should_create_product_and_return_201_when_request_is_valid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A supplier with a valid token and valid payload receives 201 with product data."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        payload = {
            "name": faker.word(),
            "description": faker.text(max_nb_chars=100),
            "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
            "unit_price": "10.50",
        }

        response = await async_client.post(
            url="/api/v1/products/",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["status"] == "success"
        assert body["message"] == "Product created successfully."

        assert body["data"]["name"] == payload["name"]
        assert body["data"]["description"] == payload["description"]
        assert body["data"]["unit_of_measure"] == payload["unit_of_measure"]
        assert Decimal(body["data"]["unit_price"]) == Decimal(payload["unit_price"])

        assert body["data"]["supplier_id"] == str(created_supplier.id)
        assert body["data"]["is_active"] is True

        assert body["data"]["id"] is not None
        assert body["data"]["created_at"] is not None
        assert body["data"]["updated_at"] is not None

    @pytest.mark.asyncio
    async def test_should_associate_product_with_authenticated_supplier(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The supplier_id in the response must match the authenticated user's ID."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["data"]["supplier_id"] == str(created_supplier.id)

    @pytest.mark.asyncio
    async def test_should_set_is_active_true_on_newly_created_product(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A freshly created product must always be active."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
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
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
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
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
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
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
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
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
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
        """A token with the ADMIN role must be rejected — only SUPPLIER may create products."""
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
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert body["status"] == "error"

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

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": "  ",
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Product name is invalid."
        assert body["context"]["name"] == "  "
        assert any("empty" in detail.lower() for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_product_name_is_too_short(
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

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": "AB",
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Product name is invalid."
        assert body["context"]["name"] == "AB"
        assert any("3 characters" in detail for detail in body["details"])

    @pytest.mark.asyncio
    async def test_should_return_400_when_product_name_is_too_long(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """A name of 150 or more characters must be rejected with 400."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        long_name = "P" * 150

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": long_name,
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Product name is invalid."
        assert any("150 characters" in detail for detail in body["details"])

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

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "-10.00",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        body = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert body["status"] == "error"
        assert body["message"] == "Unit price is invalid."
        assert any("negative" in detail.lower() for detail in body["details"])

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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_description_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the description field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_unit_of_measure_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the unit_of_measure field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_unit_price_field_is_missing(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """Omitting the unit_price field must fail Pydantic schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
            },
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
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_return_422_when_unit_of_measure_is_invalid(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """An invalid unit_of_measure value must fail schema validation."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        response = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": "INVALID",
                "unit_price": "10.50",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_should_allow_supplier_to_create_multiple_products(
        self,
        async_client: AsyncClient,
        faker: Faker,
        created_supplier: UserEntity,
        plain_password_valid: PlainPasswordVO,
        access_token_factory: Callable[[str, str], Awaitable[str]],
    ) -> None:
        """The same supplier can create several products; each gets a unique ID."""
        access_token = await access_token_factory(
            str(created_supplier.email),
            str(plain_password_valid),
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        first = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.UNIT.value,
                "unit_price": "10.50",
            },
            headers=headers,
        )

        second = await async_client.post(
            url="/api/v1/products/",
            json={
                "name": faker.word(),
                "description": faker.text(max_nb_chars=100),
                "unit_of_measure": UnitOfMeasureEnum.KG.value,
                "unit_price": "25.00",
            },
            headers=headers,
        )

        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_201_CREATED
        assert first.json()["data"]["id"] != second.json()["data"]["id"]
