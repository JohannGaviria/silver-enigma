"""Unit tests for the ToggleWarehouseStatusUseCase."""

from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.application.dtos.toggle_warehouse_status_dto import (
    ToggleWarehouseStatusCommandDto,
    ToggleWarehouseStatusResponseDto,
)
from src.modules.warehouses.application.use_cases.toggle_warehouse_status_use_case import (
    ToggleWarehouseStatusUseCase,
)
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    WarehouseHasActiveOrdersException,
    WarehouseNotFoundException,
    WarehouseRepositoryException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from tests.unit.conftest import _make_warehouse_entity


def _make_use_case(
    logger_factory_mock: Mock,
    warehouse_lifecycle_uow_mock: MagicMock,
    cache_outbound_mock: AsyncMock,
) -> ToggleWarehouseStatusUseCase:
    """Instantiate ToggleWarehouseStatusUseCase with the provided mocks."""
    return ToggleWarehouseStatusUseCase(
        logger_factory_outbound=logger_factory_mock,
        warehouse_lifecycle_unit_of_work=warehouse_lifecycle_uow_mock,
        cache_outbound=cache_outbound_mock,
    )


class TestToggleWarehouseStatusUseCase:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("is_active", [True, False])
    async def test_should_toggle_and_persist_warehouse_status_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        is_active: bool,
    ) -> None:
        """A valid command must update warehouse status, persist changes and return the response DTO."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=is_active,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.assert_awaited_once_with(
            existing.id
        )
        warehouse_lifecycle_uow_mock.warehouses.update.assert_awaited_once()
        warehouse_lifecycle_uow_mock.commit.assert_awaited_once()

        assert isinstance(result, ToggleWarehouseStatusResponseDto)
        assert result.id == existing.id
        assert result.supplier_id == existing.supplier_id
        assert result.is_active == is_active

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Only suppliers may toggle warehouse statuses."""
        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_admin(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Admins must not be allowed to toggle warehouse statuses."""
        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_touch_repository_or_cache_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Repository and cache must not be accessed when authorization fails."""
        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.assert_not_awaited()
        warehouse_lifecycle_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A missing warehouse must raise WarehouseNotFoundException."""
        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = None

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(WarehouseNotFoundException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_or_cache_when_warehouse_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """No update nor cache invalidation should occur when warehouse does not exist."""
        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = None

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(WarehouseNotFoundException):
            await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_does_not_belong_to_authenticated_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A warehouse owned by another supplier must be rejected."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_warehouse_entity(faker, owner_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_or_cache_when_warehouse_belongs_to_different_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """No update nor cache invalidation should occur on ownership mismatch."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_warehouse_entity(faker, owner_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_update_persistence_fails(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Repository exceptions raised during update must propagate."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )
        warehouse_lifecycle_uow_mock.warehouses.update.side_effect = (
            WarehouseRepositoryException("DB error")
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(WarehouseRepositoryException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_invalidate_cache_exactly_once_on_successful_toggle(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Cache must be invalidated exactly once during a successful toggle."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        await use_case.execute(command, authenticated_user)

        cache_outbound_mock.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_use_supplier_id_in_cache_invalidation_key(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The cache key must contain the authenticated supplier ID."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        await use_case.execute(command, authenticated_user)

        cache_key = cache_outbound_mock.delete.await_args.args[0]

        assert str(supplier_id) in str(cache_key)

    @pytest.mark.asyncio
    async def test_should_return_toggle_warehouse_status_response_dto_instance(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The use case must always return a ToggleWarehouseStatusResponseDto."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            None
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        assert isinstance(result, ToggleWarehouseStatusResponseDto)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            OrderStatusEnum.CONFIRMED,
            OrderStatusEnum.PROCESSING,
            OrderStatusEnum.SHIPPED,
        ],
    )
    async def test_should_raise_exception_when_warehouse_has_active_orders(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        status: OrderStatusEnum,
    ) -> None:
        """Warehouse cannot be deactivated when it has active orders."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        order = Mock()
        order.order_status = status

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            order
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        with pytest.raises(WarehouseHasActiveOrdersException):
            await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.update.assert_not_awaited()
        warehouse_lifecycle_uow_mock.commit.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            OrderStatusEnum.DRAFT,
            OrderStatusEnum.DELIVERED,
            OrderStatusEnum.CANCELLED,
        ],
    )
    async def test_should_allow_toggle_when_order_status_is_not_blocking(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_lifecycle_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        status: OrderStatusEnum,
    ) -> None:
        """Warehouse can be deactivated when orders are not in blocking statuses."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)

        order = Mock()
        order.order_status = status

        warehouse_lifecycle_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_lifecycle_uow_mock.orders_query.find_by_warehouse_id.return_value = (
            order
        )

        command = ToggleWarehouseStatusCommandDto(
            warehouse_id=existing.id,
            is_active=False,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock,
            warehouse_lifecycle_uow_mock,
            cache_outbound_mock,
        )

        await use_case.execute(command, authenticated_user)

        warehouse_lifecycle_uow_mock.warehouses.update.assert_awaited_once()
        warehouse_lifecycle_uow_mock.commit.assert_awaited_once()
        cache_outbound_mock.delete.assert_awaited_once()
