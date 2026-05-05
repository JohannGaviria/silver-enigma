from datetime import UTC
from uuid import UUID

import pytest
from faker import Faker

from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.exception import InvalidTokenPayloadException
from src.shared.domain.value_objects.token_payload_vo import TokenPayloadVO


class TestTokenPayloadVO:
    def test_should_create_token_payload_when_valid_data_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the TokenPayloadVO is created successfully when valid data is provided."""
        jti = UUID(faker.uuid4())
        sub = UUID(faker.uuid4())
        exp = faker.future_datetime(tzinfo=UTC)

        token_payload_vo = TokenPayloadVO(
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
        """Test that the TokenPayloadVO raises an InvalidTokenPayloadException.

        when the jti is none.
        """
        with pytest.raises(InvalidTokenPayloadException):
            TokenPayloadVO(
                jti=None,  # type: ignore
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_sub_is_none(self, faker: Faker) -> None:
        """Test that the TokenPayloadVO raises an InvalidTokenPayloadException.

        when the sub is none.
        """
        with pytest.raises(InvalidTokenPayloadException):
            TokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=None,  # type: ignore
                role=UserRoleEnum.ADMIN,
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_role_is_none(self, faker: Faker) -> None:
        """Test that the TokenPayloadVO raises an InvalidTokenPayloadException.

        when the role is None.
        """
        with pytest.raises(InvalidTokenPayloadException):
            TokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=None,  # type: ignore
                exp=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_expiration_date_is_in_the_past(
        self, faker: Faker
    ) -> None:
        """Test that the TokenPayloadVO raises an InvalidTokenPayloadException.

        when the expiration date is in the past.
        """
        with pytest.raises(InvalidTokenPayloadException):
            TokenPayloadVO(
                jti=UUID(faker.uuid4()),
                sub=UUID(faker.uuid4()),
                role=UserRoleEnum.ADMIN,
                exp=faker.past_datetime(tzinfo=UTC),
            )
