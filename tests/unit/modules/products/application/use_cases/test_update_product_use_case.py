from decimal import Decimal
from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.update_product_dto import (
    UpdateProductCommandDto,
    UpdatedProductResponseDto,
)
from src.modules.products.application.use_cases.update_product_use_case import (
    UpdateProductUseCase,
)
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.exceptions.product_exception import (
    InvalidProductNameException,
    InvalidUnitPriceException,
    ProductNotFoundException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from tests.unit.conftest import _make_product_entity


def _make_use_case(
    logger_factory_mock: Mock,
    product_uow_mock: MagicMock,
) -> UpdateProductUseCase:
    """Instantiate UpdateProductUseCase with the provided mocks."""
    return UpdateProductUseCase(
        logger_factory_outbound=logger_factory_mock,
        product_unit_of_work=product_uow_mock,
    )


class TestUpdateProductUseCase:
    @pytest.mark.asyncio
    async def test_should_update_product_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """A valid command for an existing owned product must update, persist, and return the DTO."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            name="Updated Product",
            description="Updated Description",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("250.75"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        product_uow_mock.products.find_by_id.assert_awaited_once_with(existing.id)
        product_uow_mock.products.update.assert_awaited_once()
        product_uow_mock.commit.assert_awaited_once()

        assert isinstance(result, UpdatedProductResponseDto)
        assert result.id == existing.id
        assert result.supplier_id == supplier_id
        assert result.name == "Updated Product"
        assert result.description == "Updated Description"
        assert result.unit_of_measure == UnitOfMeasureEnum.KG
        assert result.unit_price == Decimal("250.75")

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """A non-SUPPLIER role must be rejected before any repository interaction."""
        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_touch_repository_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Repository operations must not be executed when authorization fails."""
        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        product_uow_mock.products.find_by_id.assert_not_awaited()
        product_uow_mock.products.update.assert_not_awaited()
        product_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When find_by_id returns None a ProductNotFoundException must be raised."""
        product_uow_mock.products.find_by_id.return_value = None

        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
            name=faker.company(),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(ProductNotFoundException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_when_product_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Neither update nor commit should occur when the product is not found."""
        product_uow_mock.products.find_by_id.return_value = None

        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(ProductNotFoundException):
            await use_case.execute(command, authenticated_user)

        product_uow_mock.products.update.assert_not_awaited()
        product_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_belongs_to_another_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """A product owned by a different supplier must raise InsufficientPermissionsException."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_when_product_belongs_to_different_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Neither update nor commit should occur on an ownership mismatch."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        product_uow_mock.products.update.assert_not_awaited()
        product_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_name",
        ["", " ", "a", "ab", "a" * 150],
    )
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
        invalid_name: str,
    ) -> None:
        """Every invalid name variant must raise InvalidProductNameException."""
        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
            name=invalid_name,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InvalidProductNameException):
            await use_case.execute(command, authenticated_user)

        product_uow_mock.products.find_by_id.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_price",
        [
            Decimal("-0.01"),
            Decimal("-1"),
            Decimal("-100"),
        ],
    )
    async def test_should_raise_exception_when_unit_price_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
        invalid_price: Decimal,
    ) -> None:
        """Every negative unit price variant must raise InvalidUnitPriceException."""
        command = UpdateProductCommandDto(
            product_id=UUID(faker.uuid4()),
            unit_price=invalid_price,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        with pytest.raises(InvalidUnitPriceException):
            await use_case.execute(command, authenticated_user)

        product_uow_mock.products.find_by_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_keep_existing_values_when_optional_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When no optional fields are provided the entity must retain its original values."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        assert result.name == str(existing.name)
        assert result.description == existing.description
        assert result.unit_of_measure == existing.unit_of_measure
        assert result.unit_price == existing.unit_price.value()

    @pytest.mark.asyncio
    async def test_should_update_only_name_when_other_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When only name is given the remaining product fields must remain unchanged."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            name="Updated Name",
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert result.name == "Updated Name"
        assert result.description == existing.description

    @pytest.mark.asyncio
    async def test_should_update_only_description_when_other_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When only description is given the remaining product fields must remain unchanged."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            description="Updated Description",
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert result.description == "Updated Description"
        assert result.name == str(existing.name)

    @pytest.mark.asyncio
    async def test_should_update_only_unit_of_measure_when_other_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When only unit_of_measure is given the remaining product fields must remain unchanged."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            unit_of_measure=UnitOfMeasureEnum.KG,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert result.unit_of_measure == UnitOfMeasureEnum.KG

    @pytest.mark.asyncio
    async def test_should_update_only_unit_price_when_other_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """When only unit_price is given the remaining product fields must remain unchanged."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            unit_price=Decimal("999.99"),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert result.unit_price == Decimal("999.99")

    @pytest.mark.asyncio
    async def test_should_preserve_immutable_fields_in_response(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Immutable fields must remain unchanged after a successful update."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            name="Updated Product",
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert result.id == existing.id
        assert result.supplier_id == existing.supplier_id
        assert result.is_active == existing.is_active
        assert result.created_at == existing.created_at

    @pytest.mark.asyncio
    async def test_should_return_updated_product_response_dto_instance(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """The use case must always return an UpdatedProductResponseDto instance."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            name="Updated Product",
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert isinstance(result, UpdatedProductResponseDto)

    @pytest.mark.asyncio
    async def test_should_commit_exactly_once_on_successful_update(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Commit must be executed exactly once during a successful update."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(faker, supplier_id)
        product_uow_mock.products.find_by_id.return_value = existing

        command = UpdateProductCommandDto(
            product_id=existing.id,
            name="Updated Product",
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        product_uow_mock.commit.assert_awaited_once()
