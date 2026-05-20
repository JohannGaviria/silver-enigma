from datetime import UTC
from uuid import UUID

import pytest
from faker import Faker

from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import InvalidAccessTokenPayloadException
from src.shared.domain.value_objects.access_token_payload_vo import AccessTokenPayloadVO


class TestAccessTokenPayloadVO:
    def test_should_create_token_payload_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the AccessTokenPayloadVO is created successfully when valid data is provided."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())
        exp = faker.future_datetime(tzinfo=UTC)

        token_payload_vo = AccessTokenPayloadVO(
            jti=jti,
            sub=sub,
            role=UserRoleEnum.ADMIN,
            exp=exp,
        )

        assert token_payload_vo.jti == jti
        assert token_payload_vo.sub == sub
        assert token_payload_vo.role == UserRoleEnum.ADMIN
        assert token_payload_vo.exp == exp

    def test_should_raise_exception_when_jti_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the jti is None.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=None,  # type: ignore
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    @pytest.mark.parametrize("jti", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_jti_is_not_a_uuid(
        self, faker: Faker, jti: str | int
    ) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the jti is not a valid UUID.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=jti,  # type: ignore
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_sub_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the sub is None.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=None,  # type: ignore
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    @pytest.mark.parametrize("sub", ["", "123", 123, "abc-123"])
    def test_should_raise_exception_when_sub_is_not_a_uuid(
        self, faker: Faker, sub: str | int
    ) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the sub is not a valid UUID.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=sub,  # type: ignore
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_role_is_none(self, faker: Faker) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the role is None.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=None,  # type: ignore
                exp=faker.future_datetime(tzinfo=UTC),
            )

    @pytest.mark.parametrize("role", ["", "ADMIN", 1, "invalid-role"])
    def test_should_raise_exception_when_role_is_not_a_user_role_enum(
        self, faker: Faker, role: str | int
    ) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the role is not a valid UserRoleEnum.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=role,  # type: ignore
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_expiration_date_is_in_the_past(
        self, faker: Faker
    ) -> None:
        """Test that the AccessTokenPayloadVO raises an InvalidAccessTokenPayloadException.

        when the expiration date is in the past.
        """
        with pytest.raises(InvalidAccessTokenPayloadException):
            AccessTokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
                exp=faker.past_datetime(tzinfo=UTC),
            )
