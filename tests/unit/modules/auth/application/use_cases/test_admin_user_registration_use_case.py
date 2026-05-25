from unittest.mock import MagicMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.admin_user_registration_dto import (
    AdminUserRegistrationCommandDto,
)
from src.modules.auth.application.use_cases.admin_user_registration_use_case import (
    AdminUserRegistrationUseCase,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
    InvalidNameException,
    InvalidPasswordHashException,
    InvalidPlainPasswordException,
)
from src.modules.auth.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.modules.auth.domain.exceptions.user_exception import (
    UserAlreadyExistsException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.shared.domain.enums.user_role_enum import UserRoleEnum


class TestAdminUserRegistrationUseCase:
    @pytest.mark.asyncio
    async def test_should_register_user_successfully_when_command_is_valid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash: str,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method registers a user successfully.

        when the command is valid.
        """
        user_uow_mock.users.find_by_email.return_value = None

        password_hash_outbound_mock.hash.return_value = password_hash

        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(),
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        result = await use_case.execute(command)

        user_uow_mock.users.save.assert_awaited_once()
        user_uow_mock.commit.assert_awaited_once()

        saved_user = user_uow_mock.users.save.await_args.args[0]

        assert isinstance(saved_user, UserEntity)

        assert str(saved_user.name) == command.name
        assert str(saved_user.email) == command.email
        assert str(saved_user.password) == password_hash
        assert saved_user.role == command.role

        assert result.id == saved_user.id
        assert result.name == command.name
        assert result.email == command.email
        assert result.role == command.role
        assert result.created_at == saved_user.created_at
        assert result.updated_at == saved_user.updated_at

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_already_exists(
        self,
        faker: Faker,
        user_uow_mock: MagicMock,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
    ) -> None:
        """Test that the execute method raises a UserAlreadyExistsException.

        when the user already exists.
        """
        existing_user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = existing_user

        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(),
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(command)

        user_uow_mock.users.save.assert_not_awaited()
        user_uow_mock.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_actor_is_not_admin(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method raises an.

        InsufficientPermissionsException when the actor is not an admin.
        """
        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(),
            role=UserRoleEnum.BUYER,
            actor_role=UserRoleEnum.SUPPLIER,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InsufficientPermissionsException):
            await use_case.execute(command)

        user_uow_mock.users.find_by_email.assert_not_awaited()
        user_uow_mock.users.save.assert_not_awaited()
        user_uow_mock.commit.assert_not_awaited()

        password_hash_outbound_mock.hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_email_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method raises an InvalidEmailException.

        when the email is invalid.
        """
        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email="invalid-email",
            password=faker.password(),
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidEmailException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_password_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method raises an.

        InvalidPlainPasswordException when the password is invalid.
        """
        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password="123",
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidPlainPasswordException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method raises an InvalidNameException.

        when the name is invalid.
        """
        command = AdminUserRegistrationCommandDto(
            name="",
            email=faker.email(),
            password=faker.password(),
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_propagate_exception_when_password_hashing_fails(
        self,
        faker: Faker,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        password_hash_outbound_mock: Mock,
    ) -> None:
        """Test that the execute method propagates the exception.

        when password hashing fails.
        """
        user_uow_mock.users.find_by_email.return_value = None

        password_hash_outbound_mock.hash.side_effect = InvalidPasswordHashException(
            "Failed to hash password"
        )

        command = AdminUserRegistrationCommandDto(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(),
            role=UserRoleEnum.ADMIN,
            actor_role=UserRoleEnum.ADMIN,
        )

        use_case = AdminUserRegistrationUseCase(
            logger_factory_outbound=logger_factory_mock,
            user_unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidPasswordHashException):
            await use_case.execute(command)

        user_uow_mock.users.save.assert_not_awaited()
        user_uow_mock.commit.assert_not_awaited()
