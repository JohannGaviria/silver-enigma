from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.application.dtos.update_warehouse_dto import (
    UpdateWarehouseCommandDto,
    UpdateWarehouseResponseDto,
)
from src.modules.warehouses.application.use_cases.update_warehouse_use_case import (
    UpdateWarehouseUseCase,
)
from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseAddressException,
    InvalidWarehouseNameException,
    WarehouseNotFoundException,
    WarehouseRepositoryException,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from tests.unit.conftest import _make_warehouse_entity


def _make_use_case(
    logger_factory_mock: Mock,
    warehouse_uow_mock: MagicMock,
    cache_outbound_mock: AsyncMock,
) -> UpdateWarehouseUseCase:
    """Instantiate UpdateWarehouseUseCase with the provided mocks."""
    return UpdateWarehouseUseCase(
        logger_factory_outbound=logger_factory_mock,
        warehouse_unit_of_work=warehouse_uow_mock,
        cache_outbound=cache_outbound_mock,
    )


class TestUpdateWarehouseUseCase:
    @pytest.mark.asyncio
    async def test_should_update_and_persist_warehouse_and_return_response_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A valid command for an existing owned warehouse must update, persist, and return the DTO."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        new_name = faker.company()
        new_address = faker.address()
        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=new_name,
            address=new_address,
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.find_by_id.assert_awaited_once_with(existing.id)
        warehouse_uow_mock.warehouses.update.assert_awaited_once()

        assert isinstance(result, UpdateWarehouseResponseDto)
        assert result.id == existing.id
        assert result.supplier_id == supplier_id
        assert result.name == new_name
        assert result.address == new_address
        assert result.is_active == existing.is_active

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A non-SUPPLIER role must be rejected before any repository interaction."""
        command = UpdateWarehouseCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_admin(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """An ADMIN role must also be rejected — only SUPPLIER may update warehouses."""
        command = UpdateWarehouseCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            name=faker.company(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_touch_repository_or_cache_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Repository and cache must not be accessed when authorization fails."""
        command = UpdateWarehouseCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            name=faker.company(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.find_by_id.assert_not_awaited()
        warehouse_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_field",
        ["name", "address"],
    )
    async def test_should_not_update_warehouse_when_command_data_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        invalid_field: str,
    ) -> None:
        """An invalid name or address VO must raise a domain exception before persisting."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        invalid_value = "x"  # too short for both name and address VOs

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=invalid_value if invalid_field == "name" else faker.company(),
            address=invalid_value if invalid_field == "address" else faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        expected_exc = (
            InvalidWarehouseNameException
            if invalid_field == "name"
            else InvalidWarehouseAddressException
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(expected_exc):
            await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.update.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_name",
        ["", "  ", "a", "ab", "a" * 100],
    )
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        invalid_name: str,
    ) -> None:
        """Every invalid name variant must raise InvalidWarehouseNameException."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=invalid_name,
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InvalidWarehouseNameException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_address",
        ["", "  ", "a", "ab", "a" * 255],
    )
    async def test_should_raise_exception_when_address_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
        invalid_address: str,
    ) -> None:
        """Every invalid address variant must raise InvalidWarehouseAddressException."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=invalid_address,
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InvalidWarehouseAddressException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """When find_by_id returns None a WarehouseNotFoundException must be raised."""
        warehouse_uow_mock.warehouses.find_by_id.return_value = None

        command = UpdateWarehouseCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(WarehouseNotFoundException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_or_cache_when_warehouse_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Neither update nor cache invalidation should occur when the warehouse is not found."""
        warehouse_uow_mock.warehouses.find_by_id.return_value = None

        command = UpdateWarehouseCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(WarehouseNotFoundException):
            await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_does_not_belong_to_authenticated_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A warehouse owned by a different supplier must raise InsufficientPermissionsException."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_warehouse_entity(faker, owner_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,  # different supplier
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_update_or_cache_when_warehouse_belongs_to_different_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Neither update nor cache invalidation should occur on an ownership mismatch."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        existing = _make_warehouse_entity(faker, owner_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        warehouse_uow_mock.warehouses.update.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_update_persistence_fails(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A WarehouseRepositoryException raised by update must propagate to the caller."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing
        warehouse_uow_mock.warehouses.update.side_effect = WarehouseRepositoryException(
            "DB error during update."
        )

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )

        with pytest.raises(WarehouseRepositoryException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_keep_existing_warehouse_values_when_optional_fields_are_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """When no optional fields are provided the entity must retain its original name and address."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            # name and address are None (not provided)
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        assert result.name == str(existing.name)
        assert result.address == str(existing.address)

    @pytest.mark.asyncio
    async def test_should_update_only_name_when_address_is_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """When only name is given the address must remain unchanged."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        new_name = faker.company()
        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=new_name,
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        assert result.name == new_name
        assert result.address == str(existing.address)

    @pytest.mark.asyncio
    async def test_should_update_only_address_when_name_is_not_provided(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """When only address is given the name must remain unchanged."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        new_address = faker.address()
        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            address=new_address,
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        assert result.name == str(existing.name)
        assert result.address == new_address

    @pytest.mark.asyncio
    async def test_should_invalidate_cache_exactly_once_on_successful_update(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Cache must be invalidated exactly once during a successful update."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        await use_case.execute(command, authenticated_user)

        cache_outbound_mock.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_use_supplier_id_in_cache_invalidation_key(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The cache key used during invalidation must contain the authenticated supplier's ID."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        await use_case.execute(command, authenticated_user)

        cache_key = cache_outbound_mock.delete.await_args.args[0]
        assert str(supplier_id) in str(cache_key)

    @pytest.mark.asyncio
    async def test_should_preserve_immutable_fields_in_response(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Immutable fields (id, supplier_id, is_active, created_at) must not change after update."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        assert result.id == existing.id
        assert result.supplier_id == existing.supplier_id
        assert result.is_active == existing.is_active
        assert result.created_at == existing.created_at

    @pytest.mark.asyncio
    async def test_should_return_update_warehouse_response_dto_instance(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        warehouse_uow_mock: MagicMock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The use case must always return an UpdateWarehouseResponseDto."""
        supplier_id = UUID(faker.uuid4())
        existing = _make_warehouse_entity(faker, supplier_id)
        warehouse_uow_mock.warehouses.find_by_id.return_value = existing

        command = UpdateWarehouseCommandDto(
            warehouse_id=existing.id,
            name=faker.company(),
            address=faker.address(),
        )
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = _make_use_case(
            logger_factory_mock, warehouse_uow_mock, cache_outbound_mock
        )
        result = await use_case.execute(command, authenticated_user)

        assert isinstance(result, UpdateWarehouseResponseDto)
