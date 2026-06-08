from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.application.dtos.adjust_stock_dto import (
    AdjustStockCommandDto,
    AdjustStockResponseDto,
)
from src.modules.products.application.use_cases.adjust_stock_use_case import (
    AdjustStockUseCase,
)
from src.modules.products.domain.entities.stock_entity import StockEntity
from src.modules.products.domain.exceptions.inventory_warehouse_exception import (
    ReferencedWarehouseNotActiveException,
    ReferencedWarehouseNotFoundException,
)
from src.modules.products.domain.exceptions.product_exception import (
    ProductNotActiveException,
    ProductNotFoundException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import TotalStockVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from tests.unit.conftest import (
    _make_product_entity,
    _make_warehouse_entity,
)


def _make_use_case(
    logger_factory_mock: Mock,
    inventory_uow_mock: MagicMock,
) -> AdjustStockUseCase:
    """Instantiate AdjustStockUseCase with the provided mocks."""
    return AdjustStockUseCase(
        logger_factory_outbound=logger_factory_mock,
        inventory_unit_of_work=inventory_uow_mock,
    )


class TestAdjustStockUseCase:
    # ---------------------------------------------------------------------------
    # success
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_create_stock_and_return_response_when_stock_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """A new stock must be created when no stock exists for the product and warehouse."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = product
        inventory_uow_mock.stocks.find_by_product_and_warehouse_for_update.return_value = None

        command = AdjustStockCommandDto(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            inventory_uow_mock,
        ).execute(command, authenticated_user)

        inventory_uow_mock.stocks.find_by_product_and_warehouse_for_update.assert_awaited_once_with(
            product.id, warehouse.id
        )
        inventory_uow_mock.stocks.find_by_product_and_warehouse.assert_not_awaited()
        inventory_uow_mock.stocks.save.assert_awaited_once()
        inventory_uow_mock.stocks.update.assert_not_awaited()
        inventory_uow_mock.inventory_movements.save.assert_awaited_once()
        inventory_uow_mock.commit.assert_awaited_once()

        saved_stock = inventory_uow_mock.stocks.save.await_args.args[0]

        assert isinstance(result, AdjustStockResponseDto)

        assert result.id == saved_stock.id
        assert result.product_id == product.id
        assert result.warehouse_id == warehouse.id
        assert result.total_stock == 100
        assert result.available_stock == 0
        assert result.stock_disponible == 100

    @pytest.mark.asyncio
    async def test_should_update_stock_and_return_response_when_stock_already_exists(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Existing stock must be updated when found."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        existing_stock = StockEntity.create(
            product_id=product.id,
            warehouse_id=warehouse.id,
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(25),
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = product
        inventory_uow_mock.stocks.find_by_product_and_warehouse_for_update.return_value = existing_stock

        command = AdjustStockCommandDto(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=200,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        result = await _make_use_case(
            logger_factory_mock,
            inventory_uow_mock,
        ).execute(command, authenticated_user)

        inventory_uow_mock.stocks.find_by_product_and_warehouse_for_update.assert_awaited_once_with(
            product.id, warehouse.id
        )
        inventory_uow_mock.stocks.find_by_product_and_warehouse.assert_not_awaited()
        inventory_uow_mock.stocks.update.assert_awaited_once()
        inventory_uow_mock.stocks.save.assert_not_awaited()
        inventory_uow_mock.inventory_movements.save.assert_awaited_once()
        inventory_uow_mock.commit.assert_awaited_once()

        assert isinstance(result, AdjustStockResponseDto)

    @pytest.mark.asyncio
    async def test_should_commit_exactly_once_when_adjustment_is_successful(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Commit must be executed exactly once during a successful adjustment."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = product
        inventory_uow_mock.stocks.find_by_product_and_warehouse_for_update.return_value = None

        command = AdjustStockCommandDto(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        await _make_use_case(
            logger_factory_mock,
            inventory_uow_mock,
        ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_awaited_once()

    # ---------------------------------------------------------------------------
    # authorization
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "role",
        [
            UserRoleEnum.ADMIN,
            UserRoleEnum.BUYER,
        ],
    )
    async def test_should_raise_exception_when_authenticated_user_is_not_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
        role: UserRoleEnum,
    ) -> None:
        """Only suppliers may adjust stock."""
        command = AdjustStockCommandDto(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=UUID(faker.uuid4()),
            role=role,
        )

        with pytest.raises(InsufficientPermissionsException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # warehouse validations
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Missing warehouse must raise ReferencedWarehouseNotFoundException."""
        supplier_id = UUID(faker.uuid4())

        inventory_uow_mock.warehouses.find_by_id.return_value = None

        command = AdjustStockCommandDto(
            product_id=UUID(faker.uuid4()),
            warehouse_id=UUID(faker.uuid4()),
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(ReferencedWarehouseNotFoundException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_belongs_to_another_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Warehouse ownership must be validated."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse

        command = AdjustStockCommandDto(
            product_id=UUID(faker.uuid4()),
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(InsufficientPermissionsException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_warehouse_is_not_active(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Inactive warehouses must not allow stock adjustments."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        ).update_is_active(False)

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse

        command = AdjustStockCommandDto(
            product_id=UUID(faker.uuid4()),
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(ReferencedWarehouseNotActiveException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    # ---------------------------------------------------------------------------
    # product validations
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_does_not_exist(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Missing product must raise ProductNotFoundException."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = None

        command = AdjustStockCommandDto(
            product_id=UUID(faker.uuid4()),
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(ProductNotFoundException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_belongs_to_another_supplier(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Product ownership must be validated."""
        owner_id = UUID(faker.uuid4())
        requester_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=requester_id,
        )

        product = _make_product_entity(
            faker=faker,
            supplier_id=owner_id,
        )

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = product

        command = AdjustStockCommandDto(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=requester_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(InsufficientPermissionsException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_product_is_not_active(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        inventory_uow_mock: MagicMock,
    ) -> None:
        """Inactive products must not allow stock adjustments."""
        supplier_id = UUID(faker.uuid4())

        warehouse = _make_warehouse_entity(
            faker=faker,
            supplier_id=supplier_id,
        )

        product = _make_product_entity(
            faker=faker,
            supplier_id=supplier_id,
        ).update_is_active(False)

        inventory_uow_mock.warehouses.find_by_id.return_value = warehouse
        inventory_uow_mock.products.find_by_id.return_value = product

        command = AdjustStockCommandDto(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=100,
        )

        authenticated_user = AuthenticatedUserCommandDto(
            user_id=supplier_id,
            role=UserRoleEnum.SUPPLIER,
        )

        with pytest.raises(ProductNotActiveException):
            await _make_use_case(
                logger_factory_mock,
                inventory_uow_mock,
            ).execute(command, authenticated_user)

        inventory_uow_mock.commit.assert_not_awaited()
