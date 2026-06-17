from decimal import Decimal
from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.orders.application.dtos.create_order_dto import (
    CreateOrderCommandDto,
    CreateOrderResponseDto,
    ProductDetailsDto,
    ProductItemsDto,
)
from src.modules.orders.application.use_cases.create_order_use_case import (
    CreateOrderUseCase,
)
from src.modules.orders.domain.exceptions.order_exception import (
    DuplicateOrderItemsException,
    InactiveReferencedProductException,
    OrderItemsRequiredException,
    ProductsFromDifferentSuppliersException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from tests.unit.conftest import _make_referenced_product


def _make_use_case(
    logger_factory_mock: Mock,
    order_management_uow_mock: MagicMock,
) -> CreateOrderUseCase:
    """Instantiate CreateOrderUseCase."""
    return CreateOrderUseCase(
        logger_factory_outbound=logger_factory_mock,
        order_management_unit_of_work=order_management_uow_mock,
    )


class TestCreateOrderUseCase:
    @pytest.mark.asyncio
    async def test_should_create_order_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """A valid command must create order, items and status history."""
        supplier_id = UUID(faker.uuid4())
        buyer_id = UUID(faker.uuid4())

        product = _make_referenced_product(
            faker=faker,
            supplier_id=supplier_id,
        )

        order_management_uow_mock.product_query.find_by_ids.return_value = [product]

        command = CreateOrderCommandDto(
            items=[
                ProductItemsDto(
                    product_id=product.product_id,
                    quantity=2,
                )
            ]
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=buyer_id,
            role=UserRoleEnum.BUYER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            order_management_uow_mock,
        ).execute(
            command,
            authenticated_user,
        )

        assert isinstance(result, CreateOrderResponseDto)

        order_management_uow_mock.orders.save.assert_awaited_once()
        order_management_uow_mock.order_items.save_many.assert_awaited_once()
        order_management_uow_mock.orders_status_history.save.assert_awaited_once()
        order_management_uow_mock.commit.assert_awaited_once()

        assert result.buyer_id == buyer_id
        assert len(result.items) == 1

        item = result.items[0]

        assert isinstance(item, ProductDetailsDto)
        assert item.product_id == product.product_id
        assert item.name == product.name
        assert item.quantity == 2
        assert item.unit_price == Decimal("100.50")

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_is_not_buyer(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """Only buyers can create orders."""
        command = CreateOrderCommandDto(
            items=[
                ProductItemsDto(
                    product_id=UUID(faker.uuid4()),
                    quantity=1,
                )
            ]
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(InsufficientPermissionsException):
            await _make_use_case(
                logger_factory_mock,
                order_management_uow_mock,
            ).execute(
                command,
                authenticated_user,
            )

        order_management_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_order_has_no_items(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """Orders require at least one item."""
        command = CreateOrderCommandDto(items=[])

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        with pytest.raises(OrderItemsRequiredException):
            await _make_use_case(
                logger_factory_mock,
                order_management_uow_mock,
            ).execute(
                command,
                authenticated_user,
            )

        order_management_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_items_are_duplicate(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """Duplicate products cannot exist in the same order."""
        product_id = UUID(faker.uuid4())

        command = CreateOrderCommandDto(
            items=[
                ProductItemsDto(
                    product_id=product_id,
                    quantity=1,
                ),
                ProductItemsDto(
                    product_id=product_id,
                    quantity=2,
                ),
            ]
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        with pytest.raises(DuplicateOrderItemsException):
            await _make_use_case(
                logger_factory_mock,
                order_management_uow_mock,
            ).execute(
                command,
                authenticated_user,
            )

        order_management_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_is_inactive(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """Inactive products cannot be ordered."""
        inactive_product = _make_referenced_product(
            faker=faker,
            supplier_id=UUID(faker.uuid4()),
            is_active=False,
        )

        order_management_uow_mock.product_query.find_by_ids.return_value = [
            inactive_product
        ]

        command = CreateOrderCommandDto(
            items=[
                ProductItemsDto(
                    product_id=inactive_product.product_id,
                    quantity=1,
                )
            ]
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        with pytest.raises(InactiveReferencedProductException):
            await _make_use_case(
                logger_factory_mock,
                order_management_uow_mock,
            ).execute(
                command,
                authenticated_user,
            )

        order_management_uow_mock.orders.save.assert_not_awaited()
        order_management_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_products_have_different_suppliers(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        order_management_uow_mock: MagicMock,
    ) -> None:
        """Products from different suppliers cannot be ordered together."""
        product_1 = _make_referenced_product(
            faker=faker,
            supplier_id=UUID(faker.uuid4()),
        )

        product_2 = _make_referenced_product(
            faker=faker,
            supplier_id=UUID(faker.uuid4()),
        )

        order_management_uow_mock.product_query.find_by_ids.return_value = [
            product_1,
            product_2,
        ]

        command = CreateOrderCommandDto(
            items=[
                ProductItemsDto(
                    product_id=product_1.product_id,
                    quantity=1,
                ),
                ProductItemsDto(
                    product_id=product_2.product_id,
                    quantity=1,
                ),
            ]
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        with pytest.raises(ProductsFromDifferentSuppliersException):
            await _make_use_case(
                logger_factory_mock,
                order_management_uow_mock,
            ).execute(
                command,
                authenticated_user,
            )

        order_management_uow_mock.orders.save.assert_not_awaited()
        order_management_uow_mock.commit.assert_not_awaited()
