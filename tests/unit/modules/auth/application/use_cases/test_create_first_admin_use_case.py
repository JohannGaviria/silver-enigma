from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

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


class TestCreateFirstAdminUseCase:
    @pytest.mark.asyncio
    async def test_should_create_admin_when_no_admin_exists(
        self,
        faker: Faker,
        user_repository_mock: AsyncMock,
        password_hash_outbound_mock: Mock,
        password_hash: str,
    ) -> None:
        """Test that the CreateFirstAdminUseCase successfully creates an admin user.

        when no admin already exists.
        """
        user_repository_mock.exists_by_role.return_value = False
        password_hash_outbound_mock.hash.return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(), email=faker.email(), plain_password=faker.password()
        )

        user_repository_mock.save.side_effect = lambda user: user

        use_case = CreateFirstAdminUseCase(
            user_repository=user_repository_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        result = await use_case.execute(command)

        assert result.name == command.name
        assert result.email == command.email
        assert result.role == UserRoleEnum.ADMIN

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_admin_already_exists(
        self,
        faker: Faker,
        user_repository_mock: AsyncMock,
        password_hash_outbound_mock: Mock,
        password_hash: str,
    ) -> None:
        """Test that the CreateFirstAdminUseCase raises an AdminAlreadyExistsException.

        when an admin user already exists.
        """
        user_repository_mock.exists_by_role.return_value = True
        password_hash_outbound_mock.hash_return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(), email=faker.email(), plain_password=faker.password()
        )

        use_case = CreateFirstAdminUseCase(
            user_repository=user_repository_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(AdminAlreadyExistsException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_name_is_invalid(
        self,
        faker: Faker,
        user_repository_mock: AsyncMock,
        password_hash_outbound_mock: Mock,
        password_hash: str,
    ) -> None:
        """Test that the CreateFirstAdminUseCase raises an InvalidNameException.

        when the name is invalid.
        """
        user_repository_mock.exists_by_role.return_value = False
        password_hash_outbound_mock.hash_return_value = password_hash

        command = CreateFirstAdminCommand(
            name=f"{faker.name() * 5}",
            email=faker.email(),
            plain_password=faker.password(),
        )

        use_case = CreateFirstAdminUseCase(
            user_repository=user_repository_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidNameException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_email_is_invalid(
        self,
        faker: Faker,
        user_repository_mock: AsyncMock,
        password_hash_outbound_mock: Mock,
        password_hash: str,
    ) -> None:
        """Test that the CreateFirstAdminUseCase raises an InvalidEmailException.

        when the email is invalid.
        """
        user_repository_mock.exists_by_role.return_value = False
        password_hash_outbound_mock.hash_return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(), email="invalid@email", plain_password=faker.password()
        )

        use_case = CreateFirstAdminUseCase(
            user_repository=user_repository_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidEmailException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_plain_password_is_invalid(
        self,
        faker: Faker,
        user_repository_mock: AsyncMock,
        password_hash_outbound_mock: Mock,
        password_hash: str,
    ) -> None:
        """Test that the CreateFirstAdminUseCase raises an InvalidPlainPasswordException.

        when the plain password is invalid.
        """
        user_repository_mock.exists_by_role.return_value = False
        password_hash_outbound_mock.hash_return_value = password_hash

        command = CreateFirstAdminCommand(
            name=faker.name(),
            email=faker.email(),
            plain_password=faker.password(length=5),
        )

        use_case = CreateFirstAdminUseCase(
            user_repository=user_repository_mock,
            password_hash_outbound=password_hash_outbound_mock,
        )

        with pytest.raises(InvalidPlainPasswordException):
            await use_case.execute(command)
