from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_inventory_allocation_repository_adapter import (
    SQLAlchemyInventoryAllocationRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_items_repository_adapter import (
    SQLAlchemyOrderItemsRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_repository_adapter import (
    SQLAlchemyOrderRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_order_status_history_repository_adapter import (
    SQLAlchemyOrderStatusHistoryRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.unit_of_work.sqlalchemy_order_management_unit_of_work_adapter import (
    SQLAlchemyOrderManagementUnitOfWorkAdapter,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_movement_repository_adapter import (
    SQLAlchemyInventoryMovementRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_inventory_repository_adapter import (
    SQLAlchemyInventoryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_query_repository_adapter import (
    SQLAlchemyProductQueryRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_stock_repository_adapter import (
    SQLAlchemyStockRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_inventory_unit_of_work_adapter import (
    SQLAlchemyInventoryUnitOfWorkAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_lifecycle_unit_of_work_adapter import (
    SQLAlchemyProductLifecycleUnitOfWorkAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_unit_of_work_adapter import (
    SQLAlchemyProductUnitOfWorkAdapter,
)
from src.modules.warehouses.domain.entities.warehouse_entity import WarehouseEntity
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_query_repository_adapter import (
    SQLAlchemyWarehouseQueryRepositoryAdapter,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_lifecycle_unit_of_work_adapter import (
    SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter,
)
from src.modules.warehouses.infrastructure.persistence.unit_of_work.sqlalchemy_warehouse_unit_of_work_adapter import (
    SQLAlchemyWarehouseUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

# ---------------------------------------------------------------------------
# Modules: AUTH
# ---------------------------------------------------------------------------


@pytest.fixture()
def pinned_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyUserUnitOfWorkAdapter:
    """Provide a UoW pinned to the test ``db_session``.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.

    Args:
        db_session: The ``AsyncSession`` provided by the root conftest fixture.
        logger_factory_outbound: Structlog logger factory.

    Returns:
        SQLAlchemyUserUnitOfWorkAdapter: A UoW ready for integration assertions.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


# ---------------------------------------------------------------------------
# Modules: WAREHOUSES
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def warehouse_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyWarehouseRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyWarehouseRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest_asyncio.fixture()
async def warehouse_query_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyWarehouseQueryRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyWarehouseQueryRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def pinned_warehouse_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyWarehouseUnitOfWorkAdapter:
    """Warehouse UoW pinned to the test ``db_session``.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyWarehouseUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def pinned_warehouse_lifecycle_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter:
    """Warehouse Lifecycle UoW pinned to the test session."""

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyWarehouseLifecycleUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


def _make_warehouse_entity(faker: Faker, supplier_id: UUID) -> WarehouseEntity:
    """Helper to build a WarehouseEntity with valid values."""
    return WarehouseEntity.create(
        supplier_id=supplier_id,
        name=WarehouseNameVO(faker.company()),
        address=WarehouseAddressVO(faker.address()),
    )


# ---------------------------------------------------------------------------
# Modules: PRODUCTS
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture()
async def product_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyProductRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyProductRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def pinned_product_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyProductUnitOfWorkAdapter:
    """Product UoW pinned to the test session."""

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyProductUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


def _make_product_entity(
    faker: Faker,
    supplier_id: UUID,
) -> ProductEntity:
    """Helper to build a ProductEntity with valid values."""
    return ProductEntity.create(
        supplier_id=supplier_id,
        name=ProductNameVO(faker.company()),
        description=faker.text(),
        unit_of_measure=UnitOfMeasureEnum.UNIT,
        unit_price=UnitPriceVO(Decimal("1000")),
    )


@pytest_asyncio.fixture()
async def inventory_movement_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyInventoryMovementRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyInventoryMovementRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest_asyncio.fixture()
async def stock_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyStockRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyStockRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def pinned_inventory_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyInventoryUnitOfWorkAdapter:
    """Inventory UoW pinned to the test session."""

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyInventoryUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest_asyncio.fixture()
async def inventory_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyInventoryRepositoryAdapter:
    """Repository wired to the integration-test session."""
    return SQLAlchemyInventoryRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def pinned_product_lifecycle_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyProductLifecycleUnitOfWorkAdapter:
    """Product Lifecycle UoW pinned to the test session.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyProductLifecycleUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def product_query_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyProductQueryRepositoryAdapter:
    """Returns an order product query repository bound to the test session.

    This adapter implements orders' ProductQueryRepositoryPort and lives in
    the products infrastructure layer because products owns the data.
    """
    return SQLAlchemyProductQueryRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------


@pytest.fixture
def order_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyOrderRepositoryAdapter:
    """Returns an order repository bound to the test session."""
    return SQLAlchemyOrderRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def order_items_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyOrderItemsRepositoryAdapter:
    """Returns an order items repository bound to the test session."""
    return SQLAlchemyOrderItemsRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def order_status_history_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyOrderStatusHistoryRepositoryAdapter:
    """Returns an order status history repository bound to the test session."""
    return SQLAlchemyOrderStatusHistoryRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest_asyncio.fixture
async def pinned_order_management_uow(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyOrderManagementUnitOfWorkAdapter:
    """Returns an order management UoW pinned to the test transaction.

    All writes go through the same connection that the conftest transaction
    controls, so they are rolled back automatically at teardown.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return db_session

    return SQLAlchemyOrderManagementUnitOfWorkAdapter(
        session_factory=_FixedSessionMaker(),  # type: ignore[arg-type]
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture
def inventory_allocation_repository(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> SQLAlchemyInventoryAllocationRepositoryAdapter:
    """Returns an inventory allocation repository bound to the test session."""
    return SQLAlchemyInventoryAllocationRepositoryAdapter(
        session=db_session,
        logger_factory_outbound=logger_factory_outbound,
    )
