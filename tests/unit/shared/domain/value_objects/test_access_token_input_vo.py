from uuid import UUID

import pytest
from faker import Faker

from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import InvalidAccessTokenInputException
from src.shared.domain.value_objects.access_token_input_vo import AccessTokenInputVO


class TestAccessTokenInputVO:
    def test_should_create_access_token_input_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the AccessTokenInputVO is created successfully when valid data is provided."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())

        access_token_input_vo = AccessTokenInputVO(
            jti=jti,
            sub=sub,
            role=UserRoleEnum.ADMIN,
        )

        assert access_token_input_vo.jti == jti
        assert access_token_input_vo.sub == sub
        assert access_token_input_vo.role == UserRoleEnum.ADMIN

    def test_should_create_access_token_input_via_factory_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that AccessTokenInputVO.create() generates a valid VO with an auto-generated jti."""
        sub = UUID(faker.uuid4())

        access_token_input_vo = AccessTokenInputVO.create(
            sub=sub,
            role=UserRoleEnum.ADMIN,
        )

        assert isinstance(access_token_input_vo.jti, UUID)
        assert access_token_input_vo.sub == sub
        assert access_token_input_vo.role == UserRoleEnum.ADMIN

    def test_should_generate_unique_jti_on_each_factory_call(
        self, faker: Faker
    ) -> None:
        """Test that AccessTokenInputVO.create() generates a different jti on each call."""
        sub = UUID(faker.uuid4())

        first = AccessTokenInputVO.create(sub=sub, role=UserRoleEnum.ADMIN)
        second = AccessTokenInputVO.create(sub=sub, role=UserRoleEnum.ADMIN)

        assert first.jti != second.jti

    def test_should_raise_exception_when_jti_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the jti is None.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=None,  # type: ignore
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
            )

    @pytest.mark.parametrize("jti", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_jti_is_not_a_uuid(
        self, faker: Faker, jti: str | int
    ) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the jti is not a valid UUID.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=jti,  # type: ignore
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
            )

    def test_should_raise_exception_when_sub_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the sub is None.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=UUID(faker.uuid4()),
                sub=None,  # type: ignore
                role=UserRoleEnum.ADMIN,
            )

    @pytest.mark.parametrize("sub", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_sub_is_not_a_uuid(
        self, faker: Faker, sub: str | int
    ) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the sub is not a valid UUID.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=UUID(faker.uuid4()),
                sub=sub,  # type: ignore
                role=UserRoleEnum.ADMIN,
            )

    def test_should_raise_exception_when_role_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the role is None.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=None,  # type: ignore
            )

    @pytest.mark.parametrize("role", ["", "ADMIN", 1, "invalid-role"])
    def test_should_raise_exception_when_role_is_not_a_user_role_enum(
        self, faker: Faker, role: str | int
    ) -> None:
        """Test that the AccessTokenInputVO raises an InvalidAccessTokenInputException.

        when the role is not a valid UserRoleEnum.
        """
        with pytest.raises(InvalidAccessTokenInputException):
            AccessTokenInputVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=role,  # type: ignore
            )
