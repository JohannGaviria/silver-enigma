from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.application.dtos.create_warehouse_dto import (
    CreateWarehouseCommandDto,
)
from src.modules.warehouses.application.use_cases.create_warehouse_use_case import (
    CreateWarehouseUseCase,
)
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseAddressException,
    InvalidWarehouseNameException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)


class TestCreateWarehouseUseCase:
    @pytest.mark.asyncio
    async def test_should_create_warehouse_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method creates a warehouse when the command is valid."""
        command = CreateWarehouseCommandDto(
            name=faker.name(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.save.assert_awaited_once()
        warehouse_uow_mock.commit.assert_awaited_once()

        saved_warehouse = warehouse_uow_mock.warehouses.save.await_args.args[0]

        assert isinstance(saved_warehouse, WarehouseEntity)
        assert str(saved_warehouse.id) == str(result.id)
        assert str(saved_warehouse.supplier_id) == str(authenticated_user.user_id)
        assert str(saved_warehouse.name) == command.name
        assert str(saved_warehouse.address) == command.address
        assert saved_warehouse.is_active is True

        assert result.id
        assert result.supplier_id == authenticated_user.user_id
        assert result.name == command.name
        assert result.address == command.address
        assert result.is_active is True
        assert result.created_at == saved_warehouse.created_at
        assert result.updated_at == saved_warehouse.updated_at

    @pytest.mark.asyncio
    async def test_should_invalidate_supplier_warehouses_cache_before_creating_warehouse(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method invalidates the supplier warehouses.

        cache before creating the warehouse.
        """
        command = CreateWarehouseCommandDto(
            name=faker.name(),
            address=faker.address(),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        await use_case.execute(command, authenticated_user)

        cache_outbound_mock.delete.assert_awaited_once()

        cache_call = cache_outbound_mock.delete.await_args.args[0]

        assert str(authenticated_user.user_id) in str(cache_call)

        cache_outbound_mock.delete.assert_awaited_once()
        warehouse_uow_mock.warehouses.save.assert_awaited_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "name",
        [
            "",
            "  ",
            "a",
            "ab",
            "13",
            "a" * 101,
        ],
    )
    async def test_should_raise_exception_when_warehouse_name_is_invalid(
        self,
        faker: Faker,
        name: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception.

        when the warehouse name is invalid.
        """
        command = CreateWarehouseCommandDto(
            name=name,
            address=faker.address(),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        with pytest.raises(InvalidWarehouseNameException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "address",
        [
            "",
            "  ",
            "a",
            "ab",
            "13",
            "a" * 255,
        ],
    )
    async def test_should_raise_exception_when_warehouse_address_is_invalid(
        self,
        faker: Faker,
        address: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception.

        when the warehouse address is invalid.
        """
        command = CreateWarehouseCommandDto(
            name=faker.name(),
            address=address,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        with pytest.raises(InvalidWarehouseAddressException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_touch_cache_or_persist_warehouse_when_warehouse_data_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method does not touch the cache.

        or persist the warehouse when the warehouse data is invalid.
        """
        command = CreateWarehouseCommandDto(
            name="a",
            address=faker.address(),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        with pytest.raises(InvalidWarehouseNameException):
            await use_case.execute(command, authenticated_user)

        cache_outbound_mock.delete.assert_not_awaited()
        warehouse_uow_mock.warehouses.save.assert_not_awaited()
        warehouse_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: MagicMock,
        warehouse_uow_mock: MagicMock,
    ) -> None:
        """Test that the execute method raises an exception.

        when the user is not a supplier.
        """
        command = CreateWarehouseCommandDto(
            name=faker.name(),
            address=faker.address(),
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = CreateWarehouseUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_unit_of_work=warehouse_uow_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)
