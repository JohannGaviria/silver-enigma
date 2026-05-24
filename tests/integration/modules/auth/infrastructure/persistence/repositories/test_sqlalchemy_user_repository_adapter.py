from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.auth_exception import (
    UserAlreadyExistsException,
    UserRepositoryException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.infrastructure.persistence.repositories.sqlalchemy_user_repository_adapter import (
    SQLAlchemyUserRepositoryAdapter,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestSQLAlchemyUserRepositoryAdapter:
    # ---------------------------------------------------------------------------
    # Method: find_by_id
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_return_user_when_user_with_id_exists(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """find_by_id returns the user entity when the ID exists."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        await user_repository.save(user)

        result = await user_repository.find_by_id(user.id)

        assert result is not None
        assert result.id == user.id
        assert result.name == user.name
        assert result.email == user.email
        assert result.role == user.role

    @pytest.mark.asyncio
    async def test_should_return_none_when_user_with_id_does_not_exist(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """find_by_id returns None when no user exists with the given ID."""
        result = await user_repository.find_by_id(UUID(faker.uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_user_repository_exception_when_sqlalchemy_error_occurs_in_find_by_id(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """UserRepositoryException must propagate when the DB query fails."""
        with patch.object(
            user_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(UserRepositoryException):
                await user_repository.find_by_id(UUID(faker.uuid4()))

    # ---------------------------------------------------------------------------
    # Method: find_by_email
    # ---------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_should_return_user_when_user_with_email_exists(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """find_by_email returns the user entity when the email exists."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        await user_repository.save(user)

        result = await user_repository.find_by_email(user.email)

        assert result is not None
        assert result.id == user.id
        assert result.name == user.name
        assert result.email == user.email
        assert result.role == user.role

    @pytest.mark.asyncio
    async def test_should_return_none_when_user_with_email_does_not_exist(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """find_by_email returns None when no user exists with the given email."""
        email = EmailVO(faker.email())

        result = await user_repository.find_by_email(email)

        assert result is None

    @pytest.mark.asyncio
    async def test_should_raise_user_repository_exception_when_sqlalchemy_error_occurs_in_find_by_email(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """UserRepositoryException must propagate when the DB query fails."""
        with patch.object(
            user_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(UserRepositoryException):
                await user_repository.find_by_email(EmailVO(faker.email()))

    # ---------------------------------------------------------------------------
    # Method: exists_by_role
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_return_false_when_no_user_with_role_exists(
        self, user_repository: SQLAlchemyUserRepositoryAdapter
    ) -> None:
        """exists_by_role returns False when no user with the given role is in the DB."""
        result = await user_repository.exists_by_role(UserRoleEnum.ADMIN)

        assert not result

    @pytest.mark.asyncio
    async def test_should_return_true_when_user_with_role_exists(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """exists_by_role returns True after a user with that role is flushed."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        await user_repository.save(user)
        result = await user_repository.exists_by_role(UserRoleEnum.ADMIN)

        assert result

    @pytest.mark.asyncio
    async def test_should_raise_user_repository_exception_when_sqlalchemy_error_occurs_in_exists_by_role(
        self, user_repository: SQLAlchemyUserRepositoryAdapter
    ) -> None:
        """UserRepositoryException must propagate when the DB query fails."""
        with patch.object(
            user_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(UserRepositoryException):
                await user_repository.exists_by_role(UserRoleEnum.ADMIN)

    # ---------------------------------------------------------------------------
    # Method: save
    # ---------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_should_save_user_and_return_user_entity(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
        password_hash: str,
    ) -> None:
        """save() must flush the entity and return it with all fields intact."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        result = await user_repository.save(user)

        assert result.id == user.id
        assert result.name == user.name
        assert result.email == user.email
        assert result.role == user.role

    @pytest.mark.asyncio
    async def test_should_raise_user_already_exists_exception_when_saving_duplicate_email(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """UserAlreadyExistsException must be raised on a duplicate-email flush."""
        email = EmailVO(faker.email())

        user1 = UserEntity.create(
            name=NameVO(faker.name()),
            email=email,
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )
        user2 = UserEntity.create(
            name=NameVO(faker.name()),
            email=email,
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        await user_repository.save(user1)

        with pytest.raises(UserAlreadyExistsException):
            await user_repository.save(user2)

    @pytest.mark.asyncio
    async def test_should_raise_user_repository_exception_when_flush_fails_in_save(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """UserRepositoryException must be raised when ``session.flush`` fails.

        The repository calls ``flush`` (not ``commit``) — commit is the UoW's
        responsibility.  This test patches the right boundary.
        """
        with patch.object(
            user_repository.session,
            "flush",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            user = UserEntity.create(
                name=NameVO(faker.name()),
                email=EmailVO(faker.email()),
                password=PasswordHashVO(password_hash),
                role=UserRoleEnum.ADMIN,
            )

            with pytest.raises(UserRepositoryException):
                await user_repository.save(user)

    @pytest.mark.asyncio
    async def test_should_never_call_commit_on_save(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.commit()``.

        Transaction control belongs exclusively to the Unit of Work.  Calling
        commit inside the repository would bypass the UoW and break atomicity.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        with patch.object(
            user_repository.session,
            "commit",
            new=AsyncMock(),
        ) as mock_commit:
            await user_repository.save(user)

        mock_commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_never_call_rollback_on_save(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """The repository must NEVER call ``session.rollback()``.

        Rollback is also the UoW's responsibility.  The repository only
        flushes; the UoW decides whether to commit or roll back.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        with patch.object(
            user_repository.session,
            "rollback",
            new=AsyncMock(),
        ) as mock_rollback:
            await user_repository.save(user)

        mock_rollback.assert_not_awaited()
