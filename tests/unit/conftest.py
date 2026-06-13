from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

# ---------------------------------------------------------------------------
# SHARED
# ---------------------------------------------------------------------------


@pytest.fixture()
def logger_factory_mock() -> Mock:
    """Fixture that provides a mock logger factory for testing."""
    return Mock()


@pytest.fixture()
def token() -> str:
    """Fixture that provides a valid token string for testing purposes."""
    return "valid-token-123"


@pytest.fixture()
def access_token_type() -> list[str]:
    """Fixture that provides a list of valid access token types for testing."""
    return ["Bearer"]


@pytest.fixture()
def session_mock() -> AsyncMock:
    """Return an ``AsyncMock`` that behaves like an ``AsyncSession``."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture()
def session_factory_mock(session_mock: AsyncMock) -> MagicMock:
    """Return a callable mock that always yields ``session_mock`` when called."""
    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value = session_mock
    return factory


@pytest.fixture()
def token_outbound_mock() -> Mock:
    """Fixture that provides a mock token outbound adapter for testing."""
    return Mock()


@pytest.fixture()
def cache_outbound_mock() -> AsyncMock:
    """Fixture that provides a mock cache outbound adapter for testing."""
    return AsyncMock()


# ---------------------------------------------------------------------------
# Modules: AUTH
# ---------------------------------------------------------------------------


@pytest.fixture()
def password_hash() -> str:
    """Fixture that provides a hashed password for testing purposes."""
    return "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYJXRz.HV9K"


@pytest.fixture()
def user_repository_mock() -> AsyncMock:
    """Fixture that provides a mock user repository for testing."""
    return AsyncMock()


@pytest.fixture()
def password_hash_outbound_mock() -> Mock:
    """Fixture that provides a mock password hash outbound adapter for testing."""
    return Mock()


@pytest.fixture()
def uow_with_session_mock(
    session_factory_mock: MagicMock,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> tuple[SQLAlchemyUserUnitOfWorkAdapter, AsyncMock]:
    """Provide a UoW wired to a mocked session, plus the session mock itself.

    Returns:
        tuple: ``(uow, session_mock)`` so tests can assert on both objects.
    """
    uow = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=session_factory_mock,
        logger_factory_outbound=logger_factory_outbound,
    )
    return uow, session_factory_mock.return_value


@pytest.fixture()
def user_uow_mock() -> MagicMock:
    """Build a Unit-of-Work mock that behaves as an async context manager.

    The returned mock exposes ``uow.users`` (an ``AsyncMock``) with
    common repository methods preconfigured for testing.

    Returns:
        MagicMock: A UoW mock ready to be injected into the use case.
    """
    users_mock = AsyncMock()

    # CreateFirstAdminUseCase
    users_mock.exists_by_role.return_value = False
    users_mock.save.side_effect = lambda entity: entity

    # UserAuthenticationUseCase
    users_mock.find_by_email.return_value = None

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.users = users_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock


# ---------------------------------------------------------------------------
# Modules: WAREHOUSES
# ---------------------------------------------------------------------------


@pytest.fixture()
def warehouse_uow_with_session_mock(
    session_factory_mock: MagicMock,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> tuple[SQLAlchemyWarehouseUnitOfWorkAdapter, AsyncMock]:
    """Provide a warehouse UoW wired to a mocked session, plus the session mock.

    Returns:
        tuple: ``(uow, session_mock)`` so tests can assert on both objects.
    """
    uow = SQLAlchemyWarehouseUnitOfWorkAdapter(
        session_factory=session_factory_mock,
        logger_factory_outbound=logger_factory_outbound,
    )
    return uow, session_factory_mock.return_value


@pytest.fixture()
def warehouse_uow_mock() -> MagicMock:
    """Build a Unit-of-Work mock that behaves as an async context manager.

    The returned mock exposes ``uow.warehouses`` (an ``AsyncMock``) with
    common repository methods preconfigured for testing.

    Returns:
        MagicMock: A UoW mock ready to be injected into the use case.
    """
    warehouses_mock = AsyncMock()

    warehouses_mock.find_by_id.return_value = None
    warehouses_mock.find_all_by_supplier_id.return_value = []
    warehouses_mock.update.side_effect = lambda entity: entity
    warehouses_mock.save.side_effect = lambda entity: entity

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.warehouses = warehouses_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock


@pytest.fixture()
def warehouse_lifecycle_uow_mock() -> MagicMock:
    """Build a Unit-of-Work mock that behaves as an async context manager.

    The returned mock exposes ``uow.warehouses`` (an ``AsyncMock``) with
    common repository methods preconfigured for testing.

    Returns:
        MagicMock: A UoW mock ready to be injected into the use case.
    """
    warehouses_mock = AsyncMock()
    orders_query_mock = AsyncMock()

    warehouses_mock.find_by_id.return_value = None
    warehouses_mock.find_all_by_supplier_id.return_value = []
    warehouses_mock.update.side_effect = lambda entity: entity
    warehouses_mock.save.side_effect = lambda entity: entity

    orders_query_mock.exists_by_warehouse_id_and_statuses.return_value = False

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.warehouses = warehouses_mock
    uow_mock.orders_query = orders_query_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock


def _make_warehouse_entity(faker: Faker, supplier_id: UUID) -> WarehouseEntity:
    """Helper to build a WarehouseEntity with valid VOs."""
    return WarehouseEntity.create(
        supplier_id=supplier_id,
        name=WarehouseNameVO(faker.company()),
        address=WarehouseAddressVO(faker.address()),
    )


# ---------------------------------------------------------------------------
# Modules: PRODUCTS
# ---------------------------------------------------------------------------


@pytest.fixture()
def product_uow_mock() -> MagicMock:
    """Build a Product Unit-of-Work mock that behaves as an async context manager.

    Returns:
        MagicMock: A Product UoW mock ready to be injected into use cases.
    """
    products_mock = AsyncMock()

    products_mock.save.side_effect = lambda entity: entity
    products_mock.update.side_effect = lambda entity: entity
    products_mock.find_by_id.return_value = None

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.products = products_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock


@pytest.fixture()
def product_lifecycle_uow_mock() -> MagicMock:
    """Build a Product lifecycle Unit-of-Work mock that behaves as an async context manager.

    Returns:
        MagicMock: A Product lifecycle UoW mock ready to be injected into use cases.
    """
    products_mock = AsyncMock()
    orders_query_mock = AsyncMock()

    products_mock.save.side_effect = lambda entity: entity
    products_mock.update.side_effect = lambda entity: entity
    products_mock.find_by_id.return_value = None

    orders_query_mock.exists_by_product_id_and_statuses.return_value = False

    uow_mock = MagicMock()
    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.products = products_mock
    uow_mock.orders_query = orders_query_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock


def _make_product_entity(
    faker: Faker,
    supplier_id: UUID,
) -> ProductEntity:
    """Helper to build a ProductEntity with valid value objects."""
    return ProductEntity.create(
        supplier_id=supplier_id,
        name=ProductNameVO(faker.company()),
        description=faker.text(max_nb_chars=100),
        unit_of_measure=UnitOfMeasureEnum.UNIT,
        unit_price=UnitPriceVO(Decimal("100.50")),
    )


@pytest.fixture()
def inventory_uow_mock() -> MagicMock:
    """Build an Inventory Unit-of-Work mock that behaves as an async context manager.

    Returns:
        MagicMock: An Inventory UoW mock ready to be injected into use cases.
    """
    products_mock = AsyncMock()
    warehouses_mock = AsyncMock()
    stocks_mock = AsyncMock()
    inventory_movements_mock = AsyncMock()

    # Products
    products_mock.find_by_id.return_value = None
    products_mock.save.side_effect = lambda entity: entity
    products_mock.update.side_effect = lambda entity: entity

    # Warehouses
    warehouses_mock.find_by_id.return_value = None
    warehouses_mock.save.side_effect = lambda entity: entity
    warehouses_mock.update.side_effect = lambda entity: entity

    # Stocks
    stocks_mock.find_by_product_and_warehouse.return_value = None
    stocks_mock.save.side_effect = lambda entity: entity
    stocks_mock.update.side_effect = lambda entity: entity

    # Inventory movements
    inventory_movements_mock.save.side_effect = lambda entity: entity

    uow_mock = MagicMock()

    uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
    uow_mock.__aexit__ = AsyncMock(return_value=None)

    uow_mock.products = products_mock
    uow_mock.warehouses = warehouses_mock
    uow_mock.stocks = stocks_mock
    uow_mock.inventory_movements = inventory_movements_mock

    uow_mock.commit = AsyncMock()
    uow_mock.rollback = AsyncMock()

    return uow_mock
