from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.toggle_product_status_dto import (
    ToggleProductStatusCommandDto,
    ToggleProductStatusResponseDto,
)
from src.modules.products.application.use_cases.toggle_product_status_use_case import (
    ToggleProductStatusUseCase,
)
from src.modules.products.domain.exceptions.product_exception import (
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
) -> ToggleProductStatusUseCase:
    """Instantiate ToggleProductStatusUseCase with the provided mocks."""
    return ToggleProductStatusUseCase(
        logger_factory_outbound=logger_factory_mock,
        product_unit_of_work=product_uow_mock,
    )


class TestToggleProductStatusUseCase:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_active", [True, False])
    async def test_should_toggle_product_status_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
        is_active: bool,
    ) -> None:
        """A valid command must update product status, persist changes and return the response DTO."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=is_active,
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

        assert isinstance(result, ToggleProductStatusResponseDto)
        assert result.id == existing.id
        assert result.supplier_id == existing.supplier_id
        assert result.is_active == is_active

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Only suppliers may toggle product statuses."""
        command = ToggleProductStatusCommandDto(
            product_id=UUID(faker.uuid4()),
            is_active=False,
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

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_admin(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Admins must not be allowed to toggle product statuses."""
        command = ToggleProductStatusCommandDto(
            product_id=UUID(faker.uuid4()),
            is_active=False,
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
        command = ToggleProductStatusCommandDto(
            product_id=UUID(faker.uuid4()),
            is_active=False,
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
        """A missing product must raise ProductNotFoundException."""
        product_uow_mock.products.find_by_id.return_value = None

        command = ToggleProductStatusCommandDto(
            product_id=UUID(faker.uuid4()),
            is_active=False,
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
        """No update nor commit should occur when product does not exist."""
        product_uow_mock.products.find_by_id.return_value = None

        command = ToggleProductStatusCommandDto(
            product_id=UUID(faker.uuid4()),
            is_active=False,
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
        """A product owned by another supplier must be rejected."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=False,
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
        """No update nor commit should occur on ownership mismatch."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=False,
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
    async def test_should_preserve_immutable_fields_in_response(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Immutable fields must remain unchanged after a successful status toggle."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=False,
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
        assert result.name == str(existing.name)
        assert result.description == existing.description
        assert result.unit_of_measure == existing.unit_of_measure
        assert result.unit_price == existing.unit_price.value()
        assert result.created_at == existing.created_at

    @pytest.mark.asyncio
    async def test_should_return_toggle_product_status_response_dto_instance(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """The use case must always return a ToggleProductStatusResponseDto."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            product_uow_mock,
        ).execute(command, authenticated_user)

        assert isinstance(result, ToggleProductStatusResponseDto)

    @pytest.mark.asyncio
    async def test_should_commit_exactly_once_on_successful_toggle(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        product_uow_mock: MagicMock,
    ) -> None:
        """Commit must be executed exactly once during a successful toggle."""
        supplier_id = UUID(faker.uuid4())

        existing = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product_uow_mock.products.find_by_id.return_value = existing

        command = ToggleProductStatusCommandDto(
            product_id=existing.id,
            is_active=False,
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
