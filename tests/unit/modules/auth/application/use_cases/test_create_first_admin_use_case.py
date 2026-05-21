from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.create_first_admin_dto import (
    CreateFirstAdminCommand,
)
from src.modules.auth.application.use_cases.create_first_admin_use_case import (
    CreateFirstAdminUseCase,
)
from src.modules.auth.domain.exceptions.auth_exception import (
    AdminAlreadyExistsException,
    InvalidEmailException,
    InvalidNameException,
    InvalidPlainPasswordException,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestCreateFirstAdminUseCase:
    @pytest.mark.asyncio
    async def test_should_create_admin_when_no_admin_exists(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """Use case returns a valid response when no admin exists yet."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        result = await use_case.execute(command)

        assert result.name == command.name
        assert result.email == command.email
        assert result.role == UserRoleEnum.ADMIN
        assert result.id is not None
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_should_commit_transaction_after_successful_creation(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """UoW.commit() must be called exactly once on the happy path."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        await use_case.execute(command)

        user_uow_mock.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_save_user_via_uow_repository(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """uow.users.save() must be called once with a UserEntity."""
        from src.modules.auth.domain.entities.user_entity import UserEntity

        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        await use_case.execute(command)

        user_uow_mock.users.save.assert_awaited_once()
        saved_arg = user_uow_mock.users.save.call_args[0][0]
        assert isinstance(saved_arg, UserEntity)
        assert saved_arg.role == UserRoleEnum.ADMIN

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_admin_already_exists(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
    ) -> None:
        """AdminAlreadyExistsException must be raised when an admin is found."""
        password_hash_outbound_mock.hash.return_value = password_hash

        users_mock = AsyncMock()
        users_mock.exists_by_role.return_value = True
        users_mock.save.side_effect = lambda entity: entity

        uow_mock = MagicMock()
        uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
        uow_mock.__aexit__ = AsyncMock(return_value=None)
        uow_mock.users = users_mock
        uow_mock.commit = AsyncMock()
        uow_mock.rollback = AsyncMock()

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(AdminAlreadyExistsException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_not_save_user_when_admin_already_exists(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
    ) -> None:
        """uow.users.save() must NOT be called when an admin already exists."""
        password_hash_outbound_mock.hash.return_value = password_hash

        users_mock = AsyncMock()
        users_mock.exists_by_role.return_value = True
        users_mock.save.side_effect = lambda entity: entity

        uow_mock = MagicMock()
        uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
        uow_mock.__aexit__ = AsyncMock(return_value=None)
        uow_mock.users = users_mock
        uow_mock.commit = AsyncMock()
        uow_mock.rollback = AsyncMock()

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(AdminAlreadyExistsException):
            await use_case.execute(command)

        uow_mock.users.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_not_commit_when_admin_already_exists(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
    ) -> None:
        """uow.commit() must NOT be called when AdminAlreadyExistsException is raised."""
        password_hash_outbound_mock.hash.return_value = password_hash

        users_mock = AsyncMock()
        users_mock.exists_by_role.return_value = True
        users_mock.save.side_effect = lambda entity: entity

        uow_mock = MagicMock()
        uow_mock.__aenter__ = AsyncMock(return_value=uow_mock)
        uow_mock.__aexit__ = AsyncMock(return_value=None)
        uow_mock.users = users_mock
        uow_mock.commit = AsyncMock()
        uow_mock.rollback = AsyncMock()

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(AdminAlreadyExistsException):
            await use_case.execute(command)

        uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """InvalidNameException must be raised before the UoW is entered."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name="OneWordOnly",
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_name_has_more_than_four_words(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """A name with more than 4 words must raise InvalidNameException."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name="One Two Three Four Five",
            email=faker.email(),
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_email_is_invalid(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """InvalidEmailException must be raised before the UoW is entered."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email="not-an-email",
            plain_password="Secure@123",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(InvalidEmailException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_plain_password_is_invalid(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
    ) -> None:
        """InvalidPlainPasswordException must be raised before the UoW is entered."""
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password="weak",
        )

        use_case = CreateFirstAdminUseCase(
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            logger_factory_outbound=logger_factory_mock,
        )

        with pytest.raises(InvalidPlainPasswordException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()
