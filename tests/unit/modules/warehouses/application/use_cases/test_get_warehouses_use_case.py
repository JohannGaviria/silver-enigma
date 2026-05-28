from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.warehouses.application.dtos.get_warehouses_dto import (
    GetWarehousesResponseDto,
    WarehouseItemDto,
)
from src.modules.warehouses.application.use_cases.get_warehouses_use_case import (
    GetWarehousesUseCase,
)
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_by_supplier_cache_value_vo import (
    WarehouseBySupplierCacheValueVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)


def _make_warehouse_entity(faker: Faker, supplier_id: UUID) -> WarehouseEntity:
    """Helper to build a WarehouseEntity with valid VOs."""
    return WarehouseEntity.create(
        supplier_id=supplier_id,
        name=WarehouseNameVO(faker.company()),
        address=WarehouseAddressVO(faker.address()),
    )


def _make_cache_value(
    entities: list[WarehouseEntity],
) -> WarehouseBySupplierCacheValueVO:
    """Helper to build a WarehouseBySupplierCacheValueVO from a list of entities."""
    return WarehouseBySupplierCacheValueVO.from_warehouses(entities)


class TestGetWarehousesUseCase:
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """A non-SUPPLIER role must be rejected with InsufficientPermissionsException."""
        warehouse_repository_mock = AsyncMock()
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(authenticated_user)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_is_admin(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """An ADMIN role must also be rejected — only SUPPLIER may retrieve warehouses."""
        warehouse_repository_mock = AsyncMock()
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_touch_cache_or_repository_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Cache and repository must not be accessed when authorization fails."""
        warehouse_repository_mock = AsyncMock()
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(authenticated_user)

        cache_outbound_mock.get.assert_not_awaited()
        warehouse_repository_mock.find_all_by_supplier_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_return_warehouses_from_cache_when_cache_hit(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """When cache contains data the use case must return it without hitting the repository."""
        warehouse_repository_mock = AsyncMock()
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        entities = [_make_warehouse_entity(faker, supplier_id) for _ in range(2)]
        cache_value = _make_cache_value(entities)
        cache_outbound_mock.get.return_value = cache_value

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        assert isinstance(result, GetWarehousesResponseDto)
        assert len(result.warehouses) == 2
        warehouse_repository_mock.find_all_by_supplier_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_not_call_repository_when_cache_hit(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Repository must not be queried when the cache has valid data."""
        warehouse_repository_mock = AsyncMock()
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        entities = [_make_warehouse_entity(faker, supplier_id)]
        cache_outbound_mock.get.return_value = _make_cache_value(entities)

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        await use_case.execute(authenticated_user)

        warehouse_repository_mock.find_all_by_supplier_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_not_set_cache_when_cache_hit(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Cache must not be written again when a cache entry already exists."""
        warehouse_repository_mock = AsyncMock()
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        entities = [_make_warehouse_entity(faker, supplier_id)]
        cache_outbound_mock.get.return_value = _make_cache_value(entities)

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        await use_case.execute(authenticated_user)

        cache_outbound_mock.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_return_correct_warehouse_data_from_cache(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Warehouse fields returned from cache must match the cached values."""
        warehouse_repository_mock = AsyncMock()
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        entity = _make_warehouse_entity(faker, supplier_id)
        cache_outbound_mock.get.return_value = _make_cache_value([entity])

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        item = result.warehouses[0]
        assert item.id == entity.id
        assert item.supplier_id == entity.supplier_id
        assert item.name == str(entity.name)
        assert item.address == str(entity.address)
        assert item.is_active == entity.is_active

    @pytest.mark.asyncio
    async def test_should_return_empty_list_from_cache_when_supplier_has_no_warehouses(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """An empty cache value must translate to an empty warehouses list."""
        warehouse_repository_mock = AsyncMock()
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        cache_outbound_mock.get.return_value = WarehouseBySupplierCacheValueVO(
            warehouses=[]
        )

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        assert result.warehouses == []

    @pytest.mark.asyncio
    async def test_should_query_repository_when_cache_miss(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """On a cache miss the repository must be queried for the supplier's warehouses."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )
        entities = [_make_warehouse_entity(faker, supplier_id) for _ in range(3)]

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = entities
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        warehouse_repository_mock.find_all_by_supplier_id.assert_awaited_once_with(
            supplier_id
        )
        assert len(result.warehouses) == 3

    @pytest.mark.asyncio
    async def test_should_populate_cache_after_repository_query(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """After fetching from the repository the result must be stored in cache."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )
        entities = [_make_warehouse_entity(faker, supplier_id)]

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = entities
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        await use_case.execute(authenticated_user)

        cache_outbound_mock.set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_return_correct_warehouse_data_from_repository(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Warehouse fields returned from the repository must match the entity data."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )
        entity = _make_warehouse_entity(faker, supplier_id)

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = [entity]
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        item = result.warehouses[0]
        assert item.id == entity.id
        assert item.supplier_id == entity.supplier_id
        assert item.name == str(entity.name)
        assert item.address == str(entity.address)
        assert item.is_active == entity.is_active

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_supplier_has_no_warehouses_in_repository(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """An empty repository result must translate to an empty warehouses list."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = []
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        assert result.warehouses == []

    @pytest.mark.asyncio
    async def test_should_use_supplier_id_as_part_of_cache_key(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The cache key passed to the cache adapter must contain the supplier's ID."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = []
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        await use_case.execute(authenticated_user)

        cache_get_key = cache_outbound_mock.get.await_args.args[0]
        assert str(supplier_id) in str(cache_get_key)

    @pytest.mark.asyncio
    async def test_should_store_cache_entry_with_supplier_id_in_key(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The CacheEntryVO passed to cache.set must contain the supplier ID in its key."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = []
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        await use_case.execute(authenticated_user)

        cache_entry = cache_outbound_mock.set.await_args.args[0]
        assert str(supplier_id) in str(cache_entry.key)

    @pytest.mark.asyncio
    async def test_should_return_get_warehouses_response_dto_instance(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """The use case must always return a GetWarehousesResponseDto instance."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = []
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        assert isinstance(result, GetWarehousesResponseDto)

    @pytest.mark.asyncio
    async def test_should_return_warehouse_item_dtos_on_repository_path(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Each item in the response must be a WarehouseItemDto on the repository path."""
        supplier_id = UUID(faker.uuid4())
        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )
        entities = [_make_warehouse_entity(faker, supplier_id) for _ in range(2)]

        warehouse_repository_mock = AsyncMock()
        warehouse_repository_mock.find_all_by_supplier_id.return_value = entities
        cache_outbound_mock.get.return_value = None

        use_case = GetWarehousesUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            warehouse_repository=warehouse_repository_mock,
        )

        result = await use_case.execute(authenticated_user)

        for item in result.warehouses:
            assert isinstance(item, WarehouseItemDto)
