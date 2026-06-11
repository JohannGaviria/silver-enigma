from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.get_product_catalog_dto import (
    GetProductCatalogCommandDto,
)
from src.modules.products.application.use_cases.get_product_catalog_use_case import (
    GetProductCatalogUseCase,
)
from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.value_objects.product_stock_item_vo import (
    ProductStockItemVO,
)
from src.modules.products.domain.value_objects.product_stock_vo import (
    ProductStockVO,
)
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import (
    TotalStockVO,
)
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)


class TestGetProductCatalogUseCase:
    @staticmethod
    def _build_product_stock(
        faker: Faker,
    ) -> ProductStockVO:
        item = ProductStockItemVO(
            product_id=UUID(faker.uuid4()),
            name=faker.company(),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("100.50"),
            total_stock=TotalStockVO(100),
            reserved_stock=ReservedStockVO(30),
        )

        return ProductStockVO(
            products_stock=[item],
            page=1,
            page_size=10,
            elements=1,
        )

    @pytest.fixture()
    def inventory_repository_mock(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture()
    def logger_factory_mock(self) -> Mock:
        logger = Mock()

        factory = Mock()
        factory.get_logger.return_value = logger

        return factory

    @pytest.fixture()
    def use_case(
        self,
        logger_factory_mock: Mock,
        inventory_repository_mock: AsyncMock,
    ) -> GetProductCatalogUseCase:
        return GetProductCatalogUseCase(
            logger_factory_outbound=logger_factory_mock,
            inventory_repository=inventory_repository_mock,
        )

    @pytest.mark.asyncio
    async def test_should_return_product_catalog_when_authenticated_user_is_buyer(
        self,
        use_case: GetProductCatalogUseCase,
        inventory_repository_mock: AsyncMock,
        faker: Faker,
    ) -> None:
        products_stock = self._build_product_stock(faker)

        inventory_repository_mock.find_all_products_and_stock.return_value = (
            products_stock
        )

        command = GetProductCatalogCommandDto(
            name=None,
            unit_of_measure=None,
            page=1,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        result = await use_case.execute(
            command=command,
            authenticated_user=authenticated_user,
        )

        assert result.page == 1
        assert result.page_size == 10
        assert result.elements == 1

        assert len(result.products) == 1

        product = result.products[0]
        source = products_stock.products_stock[0]

        assert product.product_id == source.product_id
        assert product.name == source.name
        assert product.description == source.description
        assert product.unit_of_measure == source.unit_of_measure
        assert product.unit_price == source.unit_price
        assert product.stock_disponible == 70

    @pytest.mark.asyncio
    async def test_should_call_repository_with_expected_filters(
        self,
        use_case: GetProductCatalogUseCase,
        inventory_repository_mock: AsyncMock,
        faker: Faker,
    ) -> None:
        inventory_repository_mock.find_all_products_and_stock.return_value = (
            ProductStockVO(
                products_stock=[],
                page=2,
                page_size=20,
                elements=0,
            )
        )

        command = GetProductCatalogCommandDto(
            name="Rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            page=2,
            page_size=20,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        await use_case.execute(
            command=command,
            authenticated_user=authenticated_user,
        )

        inventory_repository_mock.find_all_products_and_stock.assert_awaited_once_with(
            name="Rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            page=2,
            page_size=20,
        )

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_supplier(
        self,
        use_case: GetProductCatalogUseCase,
        faker: Faker,
    ) -> None:
        command = GetProductCatalogCommandDto(
            name=None,
            unit_of_measure=None,
            page=1,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(InsufficientPermissionsException) as exc_info:
            await use_case.execute(
                command=command,
                authenticated_user=authenticated_user,
            )

        assert str(exc_info.value) == ("Insufficient permissions.")

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_authenticated_user_is_admin(
        self,
        use_case: GetProductCatalogUseCase,
        faker: Faker,
    ) -> None:
        command = GetProductCatalogCommandDto(
            name=None,
            unit_of_measure=None,
            page=1,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.ADMIN,
        )

        with pytest.raises(InsufficientPermissionsException) as exc_info:
            await use_case.execute(
                command=command,
                authenticated_user=authenticated_user,
            )

        assert str(exc_info.value) == ("Insufficient permissions.")

    @pytest.mark.asyncio
    async def test_should_return_empty_catalog_when_repository_returns_no_products(
        self,
        use_case: GetProductCatalogUseCase,
        inventory_repository_mock: AsyncMock,
        faker: Faker,
    ) -> None:
        inventory_repository_mock.find_all_products_and_stock.return_value = (
            ProductStockVO(
                products_stock=[],
                page=1,
                page_size=10,
                elements=0,
            )
        )

        command = GetProductCatalogCommandDto(
            name=None,
            unit_of_measure=None,
            page=1,
            page_size=10,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=UserRoleEnum.BUYER,
        )

        result = await use_case.execute(
            command=command,
            authenticated_user=authenticated_user,
        )

        assert result.products == []
        assert result.page == 1
        assert result.page_size == 10
        assert result.elements == 0
