import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommand,
)
from src.modules.auth.application.use_cases.create_first_admin_use_case import (
    CreateFirstAdminUseCase,
)
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.exceptions.auth_exception import (
    AdminAlreadyExistsException,
    InvalidEmailException,
    InvalidNameException,
    InvalidPlainPasswordException,
)
from src.modules.auth.infrastructure.outbound.argon2_password_hash_outbound_adapter import (
    Argon2PasswordHashOutboundAdapter,
)
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.infrastructure.outbound.structlog_logger_factory_outbound_adapter import (
    StructlogLoggerFactoryOutboundAdapter,
)


def _make_use_case(
    session: AsyncSession,
    logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
) -> CreateFirstAdminUseCase:
    """Wire the real adapters — same wiring as the CLI, without touching the CLI process."""
    return CreateFirstAdminUseCase(
        user_repository=SQLAlchemyUserRepositoryAdapter(
            session, logger_factory_outbound
        ),
        password_hash_outbound=Argon2PasswordHashOutboundAdapter(),
        logger_factory_outbound=logger_factory_outbound,
    )


async def _count_admins(session: AsyncSession) -> int:
    result = await session.execute(
        select(UserModel).where(UserModel.role == UserRoleEnum.ADMIN)
    )
    return len(result.scalars().all())


class TestCreateFirstAdminCLI:
    # ------------------------------------------------
    # Happy path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_create_admin_when_no_admin_exists(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """Full flow: CLI wiring creates an ADMIN row in the database."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        result = await use_case.execute(command)

        assert result.role == UserRoleEnum.ADMIN
        assert result.email == "admin@example.com"
        assert result.name == "John Doe"
        assert result.id is not None
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_should_persist_exactly_one_admin_row(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """Only one ADMIN row must exist after the CLI runs once."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        await use_case.execute(command)

        assert await _count_admins(db_session) == 1

    @pytest.mark.asyncio
    async def test_should_store_hashed_password_not_plain_text(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """The password stored in the DB must never equal the plain-text input."""
        plain_password = "Secure@123"
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password=plain_password,
        )

        await use_case.execute(command)

        row = (
            await db_session.execute(
                select(UserModel).where(UserModel.email == "admin@example.com")
            )
        ).scalar_one()

        assert row.password != plain_password
        assert row.password.startswith("$argon2")

    # ------------------------------------------------
    # Idempotency — second run must be a no-op
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_raise_admin_already_exists_when_called_twice(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """Running the CLI a second time must raise AdminAlreadyExistsException."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        await use_case.execute(command)

        with pytest.raises(AdminAlreadyExistsException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_not_create_duplicate_admin_when_called_twice(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """Even after raising, the DB must still contain exactly one ADMIN row."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        await use_case.execute(command)

        try:
            await use_case.execute(command)
        except AdminAlreadyExistsException:
            pass

        assert await _count_admins(db_session) == 1

    # ------------------------------------------------
    # Validation — domain rules enforced end-to-end
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_raise_invalid_name_when_name_has_only_one_word(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """A single-word name must be rejected before hitting the DB."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_email_when_email_format_is_wrong(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """A malformed email must be rejected before hitting the DB."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="not-an-email",
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidEmailException):
            await use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_password_when_password_is_too_weak(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """A weak password must be rejected before hitting the DB."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="John Doe",
            email="admin@example.com",
            plain_password="weak",
        )

        with pytest.raises(InvalidPlainPasswordException):
            await use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_name_when_name_has_more_than_four_words(
        self,
        db_session: AsyncSession,
        logger_factory_outbound: StructlogLoggerFactoryOutboundAdapter,
    ) -> None:
        """A name with more than 4 words must be rejected before hitting the DB."""
        use_case = _make_use_case(db_session, logger_factory_outbound)
        command = CreateFirstAdminCommand(
            name="One Two Three Four Five",
            email="admin@example.com",
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

        assert await _count_admins(db_session) == 0
