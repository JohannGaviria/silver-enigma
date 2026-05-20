import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommand,
)
from src.modules.auth.application.use_cases.create_first_admin_use_case import (
    CreateFirstAdminUseCase,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


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
def valid_admin_command(faker: Faker) -> CreateFirstAdminCommand:
    """Provide a valid CreateFirstAdminCommand with randomised data.

    Returns:
        CreateFirstAdminCommand: A command instance ready to be executed.
    """
    return CreateFirstAdminCommand(
        name=faker.name(),
        email=faker.email(),
        plain_password=faker.password(),
    )


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
