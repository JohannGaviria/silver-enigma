from decimal import Decimal
from uuid import UUID

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.repositories.sqlalchemy_product_repository_adapter import (
    SQLAlchemyProductRepositoryAdapter,
)
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_unit_of_work_adapter import (
    SQLAlchemyProductUnitOfWorkAdapter,
)
from src.modules.warehouses.infrastructure.persistence.repositories.sqlalchemy_warehouse_repository_adapter import (
    SQLAlchemyWarehouseRepositoryAdapter,
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
