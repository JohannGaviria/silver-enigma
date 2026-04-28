from unittest.mock import AsyncMock, patch

import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
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


class TestSQLAlchemyUserRepositoryAdapter:
    # ================================================
    # Method: exists_by_role
    # ================================================

    @pytest.mark.asyncio
    async def test_should_return_false_when_no_user_with_role_exists(
        self, user_repository: SQLAlchemyUserRepositoryAdapter
    ) -> None:
        """Test that the exists_by_role method returns False when no user.

        with the specified role exists in the database.
        """
        result = await user_repository.exists_by_role(UserRoleEnum.ADMIN)

        assert not result

    @pytest.mark.asyncio
    async def test_should_return_true_when_user_with_role_exists(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """Test that the exists_by_role method returns True when a user.

        with the specified role exists in the database.
        """
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
    async def test_should_raise_runtime_error_when_sqlalchemy_error_occurs_in_exists_by_role(
        self, user_repository: SQLAlchemyUserRepositoryAdapter
    ) -> None:
        """Test that the exists_by_role method raises a UserRepositoryException.

        when a SQLAlchemyError occurs during the database query.
        """
        with patch.object(
            user_repository.session,
            "execute",
            new=AsyncMock(side_effect=SQLAlchemyError("boom")),
        ):
            with pytest.raises(UserRepositoryException):
                await user_repository.exists_by_role(UserRoleEnum.ADMIN)

    # ================================================
    # Method: save
    # ================================================

    @pytest.mark.asyncio
    async def test_should_save_user_and_return_user_entity(
        self,
        faker: Faker,
        user_repository: SQLAlchemyUserRepositoryAdapter,
        password_hash: str,
    ) -> None:
        """Test that the save method successfully saves a UserEntity.

        to the database and returns the saved UserEntity with an assigned ID.
        """
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
    async def test_should_raise_value_error_when_saving_user_with_duplicate_email(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """Test that the save method raises a UserAlreadyExistsException.

        when attempting to save a UserEntity with an
        email that already exists in the database.
        """
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
    async def test_should_raise_runtime_error_when_sqlalchemy_error_occurs_in_save(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """Test that the save method raises a UserRepositoryException.

        when a SQLAlchemyError occurs during the database commit.
        """
        with patch.object(
            user_repository.session,
            "commit",
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
    async def test_should_rollback_transaction_when_commit_fails_in_save(
        self,
        faker: Faker,
        password_hash: str,
        user_repository: SQLAlchemyUserRepositoryAdapter,
    ) -> None:
        """Test that the save method rolls back the transaction.

        when a SQLAlchemyError occurs during the database commit.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        with (
            patch.object(
                user_repository.session,
                "commit",
                new=AsyncMock(side_effect=SQLAlchemyError("boom")),
            ),
            patch.object(
                user_repository.session,
                "rollback",
                new=AsyncMock(),
            ) as mock_rollback,
        ):
            with pytest.raises(UserRepositoryException):
                await user_repository.save(user)

            mock_rollback.assert_awaited_once()
