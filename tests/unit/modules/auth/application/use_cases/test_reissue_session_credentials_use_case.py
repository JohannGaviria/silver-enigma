from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from faker import Faker

from src.modules.auth.application.dtos.reissue_session_credentials_dto import (
    ReissueSessionCredentialsCommandDto,
    ReissueSessionCredentialsResponseDto,
)
from src.modules.auth.application.use_cases.reissue_session_credentials_use_case import (
    ReissueSessionCredentialsUseCase,
)
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.exceptions.session_exception import (
    SessionNotFoundException,
)
from src.modules.auth.domain.exceptions.user_exception import (
    UserNotFoundException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.refresh_token_cache_value_vo import (
    RefreshTokenCacheValueVO,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.token_exception import InvalidTokenException
from src.shared.domain.value_objects.access_token_response_vo import (
    AccessTokenResponseVO,
)
from src.shared.domain.value_objects.cache_entry_vo import CacheEntryVO
from src.shared.domain.value_objects.refresh_token_response_vo import (
    RefreshTokenResponseVO,
)
from src.shared.domain.value_objects.token_vo import TokenVO


class TestReissueSessionCredentialsUseCase:
    @pytest.mark.asyncio
    async def test_should_reissue_session_credentials_when_refresh_token_is_valid(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method reissues session credentials.

        when the refresh token is valid.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        result = await use_case.execute(command)

        assert isinstance(result, ReissueSessionCredentialsResponseDto)
        assert result.access.token == token
        assert result.access.token_type == access_token_type[0]
        assert result.access.expires_in == 3600
        assert result.refresh.token == token
        assert result.refresh.expires_in == 86400

    @pytest.mark.asyncio
    async def test_should_create_token_value_object_from_refresh_token(
        self,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method creates a TokenVO from the provided refresh token."""
        cache_outbound_mock.get.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(SessionNotFoundException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_build_cache_key_from_refresh_token(
        self,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method builds the refresh token cache key from the refresh token."""
        cache_outbound_mock.get.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(SessionNotFoundException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_get_session_from_cache_using_refresh_token_key(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method retrieves the session.

        from cache using the refresh token cache key.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        result = await use_case.execute(command)

        cache_outbound_mock.get.assert_awaited_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_session_does_not_exist(
        self,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method raises a SessionNotFoundException.

        when the session does not exist in cache.
        """
        cache_outbound_mock.get.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(SessionNotFoundException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_not_delete_refresh_token_when_session_does_not_exist(
        self,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method does not delete the refresh token.

        when the session does not exist.
        """
        cache_outbound_mock.get.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(SessionNotFoundException):
            await use_case.execute(command)

        cache_outbound_mock.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_delete_old_refresh_token_when_session_exists(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method deletes the old refresh token.

        when the session exists.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        cache_outbound_mock.delete.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_find_user_by_session_subject(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method retrieves the user associated with the session subject."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type="Bearer",
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        user_repository_mock.find_by_id.assert_awaited_once_with(user.id)

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_user_does_not_exist(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method raises a UserNotFoundException.

        when the user does not exist.
        """
        session_value = RefreshTokenCacheValueVO.create(
            sub=UUID(faker.uuid4()), expires_in=86400
        )

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(UserNotFoundException):
            await use_case.execute(command)

    @pytest.mark.asyncio
    async def test_should_not_generate_tokens_when_user_does_not_exist(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method does not generate new tokens.

        when the user does not exist.
        """
        session_value = RefreshTokenCacheValueVO.create(
            sub=UUID(faker.uuid4()), expires_in=86400
        )

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = None

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(UserNotFoundException):
            await use_case.execute(command)

        token_outbound_mock.generate_access.assert_not_called()
        token_outbound_mock.generate_refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_generate_access_token_when_user_exists(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method generates a new access token.

        when the user exists.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        token_outbound_mock.generate_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_generate_refresh_token_when_user_exists(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method generates a new refresh token.

        when the user exists.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        token_outbound_mock.generate_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_store_new_refresh_token_in_cache_when_credentials_are_reissued(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method stores the new refresh token in cache.

        when credentials are reissued.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        cache_outbound_mock.set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_create_cache_entry_with_expected_values_when_storing_refresh_token(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method creates a cache entry with the expected values.

        when storing the refresh token.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        await use_case.execute(command)

        cache_outbound_mock.set.assert_awaited_once()
        cache_entry = cache_outbound_mock.set.call_args[0][0]
        assert isinstance(cache_entry, CacheEntryVO)

    @pytest.mark.asyncio
    async def test_should_return_reissued_session_credentials_response_when_operation_succeeds(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method returns a ReissueSessionCredentialsResponseDto.

        when the operation succeeds.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.return_value = RefreshTokenResponseVO(
            refresh_token=TokenVO(token),
            expires_in=86400,
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        result = await use_case.execute(command)

        assert isinstance(result, ReissueSessionCredentialsResponseDto)
        assert result.access.token == token
        assert result.access.token_type == access_token_type[0]
        assert result.access.expires_in == 3600
        assert result.refresh.token == token
        assert result.refresh.expires_in == 86400

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_refresh_token_is_invalid(
        self,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
    ) -> None:
        """Test that the execute method raises an exception.

        when the refresh token is invalid.
        """
        command = ReissueSessionCredentialsCommandDto(
            refresh_token="",
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(InvalidTokenException):
            await use_case.execute(command)

        cache_outbound_mock.get.assert_not_awaited()
        cache_outbound_mock.delete.assert_not_awaited()
        user_repository_mock.find_by_id.assert_not_awaited()
        token_outbound_mock.generate_access.assert_not_called()
        token_outbound_mock.generate_refresh.assert_not_called()
        cache_outbound_mock.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_not_store_refresh_token_when_access_token_generation_fails(
        self,
        faker: Faker,
        token: str,
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method does not store the refresh token.

        when access token generation fails.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.side_effect = InvalidTokenException(
            "Access token generation failed"
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(InvalidTokenException):
            await use_case.execute(command)

        cache_outbound_mock.set.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_not_store_refresh_token_when_refresh_token_generation_fails(
        self,
        faker: Faker,
        token: str,
        access_token_type: list[str],
        logger_factory_mock: Mock,
        cache_outbound_mock: AsyncMock,
        token_outbound_mock: Mock,
        user_repository_mock: AsyncMock,
        password_hash: str,
    ) -> None:
        """Test that the execute method does not store the refresh token.

        when refresh token generation fails.
        """
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.BUYER,
        )

        session_value = RefreshTokenCacheValueVO.create(sub=user.id, expires_in=86400)

        cache_outbound_mock.get.return_value = session_value
        user_repository_mock.find_by_id.return_value = user

        token_outbound_mock.generate_access.return_value = AccessTokenResponseVO(
            access_token=TokenVO(token),
            token_type=access_token_type[0],
            expires_in=3600,
        )
        token_outbound_mock.generate_refresh.side_effect = InvalidTokenException(
            "Refresh token generation failed"
        )

        command = ReissueSessionCredentialsCommandDto(
            refresh_token=token,
        )

        use_case = ReissueSessionCredentialsUseCase(
            logger_factory_outbound=logger_factory_mock,
            cache_outbound=cache_outbound_mock,
            token_outbound=token_outbound_mock,
            user_repository=user_repository_mock,
        )

        with pytest.raises(InvalidTokenException):
            await use_case.execute(command)

        cache_outbound_mock.set.assert_not_awaited()
