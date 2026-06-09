from datetime import UTC
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.get_warehouse_stock_dto import (
    GetWarehouseStockCommandDto,
    GetWarehouseStockResponseDto,
    WarehouseStockItemDto,
)
from src.modules.products.application.use_cases.get_warehouse_stock_use_case import (
    GetWarehouseStockUseCase,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.modules.products.domain.value_objects.warehouse_stock_item_vo import (
    WarehouseStockItemVO,
)
from src.modules.products.domain.value_objects.warehouse_stock_vo import (
    WarehouseStockVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)


def _make_warehouse_stock_vo(faker: Faker) -> WarehouseStockVO:
    """Build a valid WarehouseStockVO for testing."""
    stock = faker.pyint(min_value=1, max_value=100)
    item = WarehouseStockItemVO(
        stock_id=UUID(faker.uuid4()),
        product_id=UUID(faker.uuid4()),
        supplier_id=UUID(faker.uuid4()),
        name=ProductNameVO("Premium Rice"),
        total_stock=TotalStockVO(stock),
        available_stock=AvailableStockVO(stock),
        stock_disponible=stock,
        created_at=faker.date_time(end_datetime=10, tzinfo=UTC),
        updated_at=faker.date_time(end_datetime=10, tzinfo=UTC),
    )

    return WarehouseStockVO(
        warehouse_stock=[item],
        page=0,
        page_size=10,
        elements=1,
    )


class TestGetWarehouseStockUseCase:
    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """Only suppliers can retrieve warehouse stock."""
        inventory_repository_mock = AsyncMock()

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

    @pytest.mark.asyncio
    async def test_should_not_call_repository_when_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """Repository must not be accessed when authorization fails."""
        inventory_repository_mock = AsyncMock()

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command, authenticated_user)

        (
            inventory_repository_mock.find_inventory_by_user_and_warehouse.assert_not_awaited()
        )

    @pytest.mark.asyncio
    async def test_should_query_repository_with_expected_parameters(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """Repository must receive the correct parameters."""
        supplier_id = UUID(faker.uuid4())
        warehouse_id = UUID(faker.uuid4())

        inventory_repository_mock = AsyncMock()
        inventory_repository_mock.find_inventory_by_user_and_warehouse.return_value = (
            WarehouseStockVO(
                warehouse_stock=[],
                page=0,
                page_size=10,
                elements=0,
            )
        )

        command = GetWarehouseStockCommandDto(
            warehouse_id=warehouse_id,
            page=1,
            page_size=25,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        await use_case.execute(command, authenticated_user)

        (
            inventory_repository_mock.find_inventory_by_user_and_warehouse.assert_awaited_once_with(
                user_id=supplier_id,
                warehouse_id=warehouse_id,
                page=1,
                page_size=25,
            )
        )

    @pytest.mark.asyncio
    async def test_should_return_get_warehouse_stock_response_dto(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """The use case must return a GetWarehouseStockResponseDto."""
        inventory_repository_mock = AsyncMock()
        inventory_repository_mock.find_inventory_by_user_and_warehouse.return_value = (
            _make_warehouse_stock_vo(faker)
        )

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        assert isinstance(result, GetWarehouseStockResponseDto)

    @pytest.mark.asyncio
    async def test_should_return_correct_stock_data(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """Response data must match the WarehouseStockVO returned by the repository."""
        warehouse_stock = _make_warehouse_stock_vo(faker)

        inventory_repository_mock = AsyncMock()
        inventory_repository_mock.find_inventory_by_user_and_warehouse.return_value = (
            warehouse_stock
        )

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        item = result.warehouse_stock[0]
        source = warehouse_stock.warehouse_stock[0]

        assert item.stock_id == source.stock_id
        assert item.product_id == source.product_id
        assert item.name == str(source.name)
        assert item.total_stock == source.total_stock.value()
        assert item.available_stock == source.available_stock.value()
        assert item.stock_disponible == source.stock_disponible
        assert item.created_at == source.created_at
        assert item.updated_at == source.updated_at

    @pytest.mark.asyncio
    async def test_should_return_warehouse_stock_item_dtos(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """Every item returned must be a WarehouseStockItemDto."""
        inventory_repository_mock = AsyncMock()
        inventory_repository_mock.find_inventory_by_user_and_warehouse.return_value = (
            _make_warehouse_stock_vo(faker)
        )

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        for item in result.warehouse_stock:
            assert isinstance(item, WarehouseStockItemDto)

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_repository_returns_no_stock(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
    ) -> None:
        """An empty WarehouseStockVO must result in an empty response list."""
        inventory_repository_mock = AsyncMock()
        inventory_repository_mock.find_inventory_by_user_and_warehouse.return_value = (
            WarehouseStockVO(
                warehouse_stock=[],
                page=0,
                page_size=10,
                elements=0,
            )
        )

        command = GetWarehouseStockCommandDto(
            warehouse_id=UUID(faker.uuid4()),
            page=0,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        use_case = GetWarehouseStockUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

        result = await use_case.execute(command, authenticated_user)

        assert result.warehouse_stock == []
