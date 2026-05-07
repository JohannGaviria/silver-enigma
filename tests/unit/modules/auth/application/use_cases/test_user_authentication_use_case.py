from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from faker import Faker

from src.modules.auth.application.dtos.user_authentication_dto import (
    UserAuthenticationCommand,
)
from src.modules.auth.application.use_cases.user_authentication_use_case import (
    UserAuthenticationUseCase,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.exceptions.auth_exception import (
    AuthenticationFailedException,
    InvalidEmailException,
    InvalidPlainPasswordException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import (
    PasswordHashVO,
)
from src.shared.domain.value_objects.access_token_response_vo import (
    AccessTokenResponseVO,
)
from src.shared.domain.value_objects.refresh_token_response_vo import (
    RefreshTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class TestUserAuthenticationUseCase:
    @pytest.mark.asyncio
    async def test_should_authenticate_user_successfully(
        self,
        faker: Faker,
        password_hash: str,
        token: str,
        access_token_type: list[str],
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Use case should return valid tokens when credentials are correct."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = True

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = UserAuthenticationCommand(
            email=str(user.email),
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        result = await use_case.execute(command)

        assert result.access.token == token
        assert result.access.token_type == access_token_type[0]
        assert result.access.expires_in == 3600

        assert result.refresh.token == token
        assert result.refresh.expires_in == 86400

    @pytest.mark.asyncio
    async def test_should_find_user_by_email(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """uow.users.find_by_email() must be called once with EmailVO."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = True

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO("access-token"),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO("refresh-token"),
            expires_in=86400,
        )

        command = UserAuthenticationCommand(
            email=str(user.email),
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        await use_case.execute(command)

        user_uow_mock.users.find_by_email.assert_awaited_once()

        email_arg = user_uow_mock.users.find_by_email.call_args[0][0]
        assert isinstance(email_arg, EmailVO)
        assert str(email_arg) == command.email

    @pytest.mark.asyncio
    async def test_should_verify_password(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """password_hash_outbound.verify() must be called once."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = True

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO("access-token"),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO("refresh-token"),
            expires_in=86400,
        )

        command = UserAuthenticationCommand(
            email=str(user.email),
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        await use_case.execute(command)

        password_hash_outbound_mock.verify.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_store_refresh_token_in_cache(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """cache_outbound.set() must be awaited once with CacheEntryVO."""
        from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO

        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = True

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO("access-token"),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO("refresh-token"),
            expires_in=86400,
        )

        command = UserAuthenticationCommand(
            email=str(user.email),
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        await use_case.execute(command)

        cache_outbound_mock.set.assert_awaited_once()

        cache_entry = cache_outbound_mock.set.call_args[0][0]
        assert isinstance(cache_entry, CacheEntryVO)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_not_found(
        self,
        faker: Faker,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """AuthenticationFailedException must be raised when user does not exist."""
        user_uow_mock.users.find_by_email.return_value = None

        command = UserAuthenticationCommand(
            email=faker.email(),
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_password_is_invalid(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """AuthenticationFailedException must be raised for invalid password."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = False

        command = UserAuthenticationCommand(
            email=str(user.email),
            password="WrongPassword@123",
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_not_generate_tokens_when_password_is_invalid(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """Token generation must not occur when password verification fails."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = False

        command = UserAuthenticationCommand(
            email=str(user.email),
            password="WrongPassword@123",
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(command)

        token_outbound_mock.generate_access.assert_not_called()
        token_outbound_mock.generate_refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_not_store_refresh_token_when_authentication_fails(
        self,
        faker: Faker,
        password_hash: str,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """cache_outbound.set() must not be called when authentication fails."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        user_uow_mock.users.find_by_email.return_value = user

        password_hash_outbound_mock.verify.return_value = False

        command = UserAuthenticationCommand(
            email=str(user.email),
            password="WrongPassword@123",
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(command)

        cache_outbound_mock.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_email_is_invalid(
        self,
        faker: Faker,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """InvalidEmailException must be raised before the UoW is entered."""
        command = UserAuthenticationCommand(
            email="not-an-email",
            password=faker.password(),
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(InvalidEmailException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_password_is_invalid_format(
        self,
        faker: Faker,
        password_hash_outbound_mock: Mock,
        logger_factory_mock: Mock,
        user_uow_mock: MagicMock,
        token_outbound_mock: Mock,
        cache_outbound_mock: AsyncMock,
    ) -> None:
        """InvalidPlainPasswordException must be raised before the UoW is entered."""
        command = UserAuthenticationCommand(
            email=faker.email(),
            password="weak",
        )

        use_case = UserAuthenticationUseCase(
            logger_factory_outbound=logger_factory_mock,
            unit_of_work=user_uow_mock,
            password_hash_outbound=password_hash_outbound_mock,
            token_outbound=token_outbound_mock,
            cache_outbound=cache_outbound_mock,
        )

        with pytest.raises(InvalidPlainPasswordException):
            await use_case.execute(command)

        user_uow_mock.__aenter__.assert_not_awaited()
