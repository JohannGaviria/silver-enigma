from decimal import Decimal
from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.create_product_dto import (
    CreateProductCommandDto,
)
from src.modules.products.application.use_cases.create_product_use_case import (
    CreateProductUseCase,
)
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.exceptions.product_exception import (
    InvalidProductNameException,
    InvalidUnitPriceException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)


class TestCreateProductUseCase:
    """Unit test suite for the CreateProductUseCase."""

    @pytest.mark.asyncio
    async def test_should_create_product_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method creates a product, persists it and returns.

        the expected response when the command is valid.
        """
        supplier_id = UUID(faker.uuid4())

        command = CreateProductCommandDto(
            name=faker.name(),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("100.50"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateProductUseCase(
            logger_factory_outbound=logger_factory_mock,
            product_unit_of_work=product_uow_mock,
        )

        response = await use_case.execute(
            command=command,
            authenticated_user=authenticated_user,
        )

        product_uow_mock.products.save.assert_awaited_once()
        product_uow_mock.commit.assert_awaited_once()

        saved_product = product_uow_mock.products.save.await_args.args[0]

        assert response.id == saved_product.id
        assert response.supplier_id == supplier_id
        assert response.name == command.name
        assert response.description == command.description
        assert response.unit_of_measure == command.unit_of_measure
        assert response.unit_price == command.unit_price
        assert response.is_active is True

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception when the authenticated user is not a supplier."""
        command = CreateProductCommandDto(
            name=faker.name(),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("100.50"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = CreateProductUseCase(
            logger_factory_outbound=logger_factory_mock,
            product_unit_of_work=product_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(
                command=command,
                authenticated_user=authenticated_user,
            )

        product_uow_mock.products.save.assert_not_called()
        product_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_name_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception when the product name is invalid."""
        command = CreateProductCommandDto(
            name="as",
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("100.50"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateProductUseCase(
            logger_factory_outbound=logger_factory_mock,
            product_unit_of_work=product_uow_mock,
        )

        with pytest.raises(InvalidProductNameException):
            await use_case.execute(
                command=command,
                authenticated_user=authenticated_user,
            )

        product_uow_mock.products.save.assert_not_called()
        product_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_unit_price_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception when the unit price is invalid."""
        command = CreateProductCommandDto(
            name=faker.name(),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("-1"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateProductUseCase(
            logger_factory_outbound=logger_factory_mock,
            product_unit_of_work=product_uow_mock,
        )

        with pytest.raises(InvalidUnitPriceException):
            await use_case.execute(
                command=command,
                authenticated_user=authenticated_user,
            )

        product_uow_mock.products.save.assert_not_called()
        product_uow_mock.commit.assert_not_awaited()
