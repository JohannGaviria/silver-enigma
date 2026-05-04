import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.infrastructure.persistence.models.user_model import UserModel
from src.modules.auth.infrastructure.persistence.unit_of_work.sqlalchemy_user_unit_of_work_adapter import (
    SQLAlchemyUserUnitOfWorkAdapter,
)


class TestSQLAlchemyUserUnitOfWorkAdapter:
    # ------------------------------------------------
    # Commit path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_commit_persists_user_to_database(
        self,
        faker: Faker,
        db_session: AsyncSession,
        password_hash: str,
        pinned_uow: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        """A user saved and committed inside the UoW must be visible in the session."""
        email = faker.email()
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(email),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        async with pinned_uow as u:
            await u.users.save(user)
            await u.commit()

        result = await db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        row = result.scalar_one_or_none()

        assert row is not None
        assert str(row.email) == email

    @pytest.mark.asyncio
    async def test_exists_by_role_returns_true_after_commit(
        self,
        faker: Faker,
        password_hash: str,
        pinned_uow: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        """After committing an ADMIN user, ``exists_by_role`` must return ``True``."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        async with pinned_uow as u:
            await u.users.save(user)
            await u.commit()

        async with pinned_uow as u:
            exists = await u.users.exists_by_role(UserRoleEnum.ADMIN)

        assert exists is True

    # ------------------------------------------------
    # Rollback path
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_rollback_discards_unsaved_changes(
        self,
        faker: Faker,
        db_session: AsyncSession,
        password_hash: str,
        pinned_uow: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        """A user saved but rolled back must NOT appear in the database."""
        email = faker.email()
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(email),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        async with pinned_uow as u:
            await u.users.save(user)
            await u.rollback()

        result = await db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_unhandled_exception_triggers_automatic_rollback(
        self,
        faker: Faker,
        db_session: AsyncSession,
        password_hash: str,
        pinned_uow: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        """An unhandled exception inside the UoW block must roll back automatically."""
        email = faker.email()
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(email),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        with pytest.raises(RuntimeError):
            async with pinned_uow as u:
                await u.users.save(user)
                raise RuntimeError("something went wrong")

        result = await db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        assert result.scalar_one_or_none() is None

    # ------------------------------------------------
    # Context manager re-use
    # ------------------------------------------------

    @pytest.mark.asyncio
    async def test_uow_can_be_reused_across_multiple_transactions(
        self,
        faker: Faker,
        db_session: AsyncSession,
        password_hash: str,
        pinned_uow: SQLAlchemyUserUnitOfWorkAdapter,
    ) -> None:
        """The same UoW instance must work correctly when used more than once."""
        email1 = faker.email()
        email2 = faker.email()

        user1 = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(email1),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )
        user2 = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(email2),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        async with pinned_uow as u:
            await u.users.save(user1)
            await u.commit()

        async with pinned_uow as u:
            await u.users.save(user2)
            await u.commit()

        result = await db_session.execute(select(UserModel))
        emails = {str(r.email) for r in result.scalars().all()}

        assert email1 in emails
        assert email2 in emails
