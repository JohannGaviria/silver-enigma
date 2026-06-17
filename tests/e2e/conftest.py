from collections.abc import Awaitable, Callable
from decimal import Decimal

import pytest
from _pytest.monkeypatch import MonkeyPatch
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommandDto,
)
from src.modules.auth.application.use_cases.create_first_admin_use_case import (
    CreateFirstAdminUseCase,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_product_order_query_repository_adapter import (
    SQLAlchemyProductOrderQueryRepositoryAdapter,
)
from src.modules.orders.infrastructure.persistence.repositories.sqlalchemy_warehouse_order_query_repository_adapter import (
    SQLAlchemyWarehouseOrderQueryRepositoryAdapter,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.enums.unit_of_measure_enum import UnitOfMeasureEnum
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.modules.products.infrastructure.persistence.unit_of_work.sqlalchemy_product_unit_of_work_adapter import (
    SQLAlchemyProductUnitOfWorkAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)

# ---------------------------------------------------------------------------
# Modules: SHARED
# ---------------------------------------------------------------------------


def _make_session_factory(session: AsyncSession) -> async_sessionmaker[AsyncSession]:
    """Return a session factory that always yields the *same* test session.

    This lets the UoW adapter participate in the test transaction that the
    conftest fixture controls, so every write is rolled back automatically
    at teardown.

    Args:
        session: The ``AsyncSession`` provided by the ``db_session`` fixture.

    Returns:
        async_sessionmaker[AsyncSession]: A factory pinned to ``session``.
    """

    class _FixedSessionMaker:
        def __call__(self) -> AsyncSession:
            return session

    return _FixedSessionMaker()  # type: ignore[return-value]


@pytest.fixture()
def plain_password_valid(faker: Faker) -> PlainPasswordVO:
    return PlainPasswordVO(faker.password())


@pytest.fixture()
async def created_user(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    faker: Faker,
    password_hash_outbound: Argon2PasswordHashOutboundAdapter,
    plain_password_valid: PlainPasswordVO,
) -> UserEntity:
    unit_of_work = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )

    async with unit_of_work as uow:
        password_hash = password_hash_outbound.hash(plain_password_valid)
        entity = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=password_hash,
            role=UserRoleEnum.ADMIN,
        )
        user = await uow.users.save(entity)
        await uow.commit()

    return user


@pytest.fixture()
async def created_supplier(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    faker: Faker,
    password_hash_outbound: Argon2PasswordHashOutboundAdapter,
    plain_password_valid: PlainPasswordVO,
) -> UserEntity:
    """Create a user with the SUPPLIER role, pinned to the test session."""
    unit_of_work = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )

    async with unit_of_work as uow:
        password_hash = password_hash_outbound.hash(plain_password_valid)
        entity = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=password_hash,
            role=UserRoleEnum.SUPPLIER,
        )
        user = await uow.users.save(entity)
        await uow.commit()

    return user


@pytest.fixture()
async def created_buyer(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    faker: Faker,
    password_hash_outbound: Argon2PasswordHashOutboundAdapter,
    plain_password_valid: PlainPasswordVO,
) -> UserEntity:
    """Create a user with the BUYER role, pinned to the test session."""
    unit_of_work = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )

    async with unit_of_work as uow:
        password_hash = password_hash_outbound.hash(plain_password_valid)

        entity = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=password_hash,
            role=UserRoleEnum.BUYER,
        )

        user = await uow.users.save(entity)
        await uow.commit()

    return user


@pytest.fixture()
def access_token_factory(
    async_client: AsyncClient,
) -> Callable[[str, str], Awaitable[str]]:

    async def _factory(email: str, password: str) -> str:
        response = await async_client.post(
            url="/api/v1/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        body = response.json()

        assert response.status_code == status.HTTP_200_OK, body

        return body["data"]["access"]["token"]

    return _factory


# ---------------------------------------------------------------------------
# Modules: AUTH
# ---------------------------------------------------------------------------


@pytest.fixture()
def create_first_admin_use_case(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    password_hash_outbound: Argon2PasswordHashOutboundAdapter,
) -> CreateFirstAdminUseCase:
    """Wire the real adapters — same wiring as the CLI, scoped to the test session.

    Args:
        db_session: The test ``AsyncSession`` (managed by the root conftest fixture).
        logger_factory_outbound: Structlog logger factory.
        password_hash_outbound: Argon2 password hash adapter.

    Returns:
        CreateFirstAdminUseCase: Fully wired use case ready for testing.
    """
    unit_of_work = SQLAlchemyUserUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )
    return CreateFirstAdminUseCase(
        unit_of_work=unit_of_work,
        password_hash_outbound=password_hash_outbound,
        logger_factory_outbound=logger_factory_outbound,
    )


@pytest.fixture()
def valid_admin_command(faker: Faker) -> CreateFirstAdminCommandDto:
    """Provide a valid CreateFirstAdminCommandDto with randomised data.

    Returns:
        CreateFirstAdminCommandDto: A command instance ready to be executed.
    """
    return CreateFirstAdminCommandDto(
        name=faker.name(),
        email=faker.email(),
        plain_password=faker.password(),
    )


# ---------------------------------------------------------------------------
# Modules: PRODUCTS
# ---------------------------------------------------------------------------


@pytest.fixture()
async def created_product(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    faker: Faker,
    created_supplier: UserEntity,
) -> ProductEntity:
    """Create a product associated with the supplier."""
    unit_of_work = SQLAlchemyProductUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )

    async with unit_of_work as uow:
        product = ProductEntity.create(
            supplier_id=created_supplier.id,
            name=ProductNameVO(faker.company()),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=UnitPriceVO(Decimal("10.50")),
        )

        saved_product = await uow.products.save(product)

        await uow.commit()

    return saved_product


@pytest.fixture()
async def created_products(
    db_session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    faker: Faker,
    created_supplier: UserEntity,
) -> list[ProductEntity]:
    """Create multiple products associated with the supplier."""
    unit_of_work = SQLAlchemyProductUnitOfWorkAdapter(
        session_factory=_make_session_factory(db_session),
        logger_factory_outbound=logger_factory_outbound,
    )

    products: list[ProductEntity] = []

    async with unit_of_work as uow:
        for _ in range(3):
            product = ProductEntity.create(
                supplier_id=created_supplier.id,
                name=ProductNameVO(faker.company()),
                description=faker.text(max_nb_chars=100),
                unit_of_measure=UnitOfMeasureEnum.UNIT,
                unit_price=UnitPriceVO(Decimal("10.50")),
            )

            saved_product = await uow.products.save(product)

            products.append(saved_product)

        await uow.commit()

    return products


# ---------------------------------------------------------------------------
# Modules: ORDERS
# ---------------------------------------------------------------------------


@pytest.fixture()
def created_product_with_active_orders(
    monkeypatch: MonkeyPatch,
) -> None:
    """Create a product with active orders."""

    async def fake_exists_by_product_id_and_statuses(
        self: object,
        product_id: object,
        statuses: object,
    ) -> bool:
        return True

    monkeypatch.setattr(
        SQLAlchemyProductOrderQueryRepositoryAdapter,
        "exists_by_product_id_and_statuses",
        fake_exists_by_product_id_and_statuses,
    )


@pytest.fixture()
def created_order_confirmed(monkeypatch: MonkeyPatch) -> None:
    """Simulate a warehouse with a confirmed active order."""

    async def fake_exists_by_warehouse_id_and_statuses(
        self: object,
        warehouse_id: object,
        statuses: object,
    ) -> bool:
        return True

    monkeypatch.setattr(
        SQLAlchemyWarehouseOrderQueryRepositoryAdapter,
        "exists_by_warehouse_id_and_statuses",
        fake_exists_by_warehouse_id_and_statuses,
    )
