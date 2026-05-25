import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommandDto,
)
from src.modules.auth.application.use_cases.create_first_admin_use_case import (
    CreateFirstAdminUseCase,
)
from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
    InvalidNameException,
    InvalidPlainPasswordException,
)
from src.modules.auth.domain.exceptions.user_exception import (
    AdminAlreadyExistsException,
)
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


async def _count_admins(session: AsyncSession) -> int:
    """Return the number of ADMIN rows visible in *session*.

    ``expire_all()`` discards stale identity-map entries so SQLAlchemy
    re-fetches from the DB on the next query.
    """
    session.expire_all()
    result = await session.execute(
        select(UserModel).where(UserModel.role == UserRoleEnum.ADMIN.value)
    )
    return len(result.scalars().all())


class TestCreateFirstAdminCLI:
    @pytest.mark.asyncio
    async def test_should_create_admin_when_no_admin_exists(
        self,
        create_first_admin_use_case: CreateFirstAdminUseCase,
        valid_admin_command: CreateFirstAdminCommandDto,
    ) -> None:
        """Full flow: creates an ADMIN row and returns the expected response."""
        result = await create_first_admin_use_case.execute(valid_admin_command)

        assert result.role == UserRoleEnum.ADMIN
        assert result.email == valid_admin_command.email
        assert result.name == valid_admin_command.name
        assert result.id is not None
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_should_persist_exactly_one_admin_row(
        self,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
        valid_admin_command: CreateFirstAdminCommandDto,
    ) -> None:
        """Only one ADMIN row must exist after the use case runs once."""
        await create_first_admin_use_case.execute(valid_admin_command)

        assert await _count_admins(db_session) == 1

    @pytest.mark.asyncio
    async def test_should_store_hashed_password_not_plain_text(
        self,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
        valid_admin_command: CreateFirstAdminCommandDto,
    ) -> None:
        """The password stored in the DB must never equal the plain-text input."""
        await create_first_admin_use_case.execute(valid_admin_command)

        row = (
            await db_session.execute(
                select(UserModel).where(UserModel.email == valid_admin_command.email)
            )
        ).scalar_one()

        assert row.password != valid_admin_command.plain_password
        assert row.password.startswith("$argon2")

    @pytest.mark.asyncio
    async def test_should_raise_admin_already_exists_when_called_twice(
        self,
        create_first_admin_use_case: CreateFirstAdminUseCase,
        valid_admin_command: CreateFirstAdminCommandDto,
    ) -> None:
        """Running the use case a second time must raise AdminAlreadyExistsException."""
        await create_first_admin_use_case.execute(valid_admin_command)

        with pytest.raises(AdminAlreadyExistsException):
            await create_first_admin_use_case.execute(valid_admin_command)

    @pytest.mark.asyncio
    async def test_should_not_attempt_save_on_second_run(
        self,
        create_first_admin_use_case: CreateFirstAdminUseCase,
        valid_admin_command: CreateFirstAdminCommandDto,
    ) -> None:
        """The second execution must be short-circuited by the exists_by_role guard."""
        save_calls: list[str] = []
        original_save = SQLAlchemyUserRepositoryAdapter.save

        async def _tracking_save(self, entity):  # type: ignore[no-untyped-def]
            save_calls.append(str(entity.email))
            return await original_save(self, entity)

        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(SQLAlchemyUserRepositoryAdapter, "save", _tracking_save)

            await create_first_admin_use_case.execute(valid_admin_command)

            try:
                await create_first_admin_use_case.execute(valid_admin_command)
            except AdminAlreadyExistsException:
                pass

        assert save_calls == [valid_admin_command.email]

    @pytest.mark.asyncio
    async def test_should_raise_invalid_name_when_name_has_only_one_word(
        self,
        faker: Faker,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
    ) -> None:
        """A single-word name must be rejected before hitting the DB."""
        command = CreateFirstAdminCommandDto(
            name="John",
            email=faker.email(),
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidNameException):
            await create_first_admin_use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_name_when_name_has_more_than_four_words(
        self,
        faker: Faker,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
    ) -> None:
        """A name with more than 4 words must be rejected before hitting the DB."""
        command = CreateFirstAdminCommandDto(
            name="One Two Three Four Five",
            email=faker.email(),
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidNameException):
            await create_first_admin_use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_email_when_email_format_is_wrong(
        self,
        faker: Faker,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
    ) -> None:
        """A malformed email must be rejected before hitting the DB."""
        command = CreateFirstAdminCommandDto(
            name=faker.name(),
            email="not-an-email",
            plain_password="Secure@123",
        )

        with pytest.raises(InvalidEmailException):
            await create_first_admin_use_case.execute(command)

        assert await _count_admins(db_session) == 0

    @pytest.mark.asyncio
    async def test_should_raise_invalid_password_when_password_is_too_weak(
        self,
        faker: Faker,
        db_session: AsyncSession,
        create_first_admin_use_case: CreateFirstAdminUseCase,
    ) -> None:
        """A weak password must be rejected before hitting the DB."""
        command = CreateFirstAdminCommandDto(
            name=faker.name(),
            email=faker.email(),
            plain_password="weak",
        )

        with pytest.raises(InvalidPlainPasswordException):
            await create_first_admin_use_case.execute(command)

        assert await _count_admins(db_session) == 0
