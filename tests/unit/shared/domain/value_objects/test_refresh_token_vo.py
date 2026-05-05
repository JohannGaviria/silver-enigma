from datetime import UTC
from uuid import UUID

import pytest
from faker import Faker

from src.shared.domain.exceptions.exception import InvalidRefreshTokenException
from src.shared.domain.value_objects.refresh_token_vo import RefreshTokenVO


class TestRefreshTokenVO:
    def test_should_create_refresh_token_when_valid_data_is_provided(
        self, faker: Faker, token: str
    ) -> None:
        """Test that the RefreshTokenVO is created successfully.

        when valid data is provided.
        """
        jti = UUID(faker.uuid4())
        user_id = UUID(faker.uuid4())
        expires_at = faker.future_datetime(tzinfo=UTC)

        refresh_token_vo = RefreshTokenVO(
            refresh_token=token, jti=jti, user_id=user_id, expires_at=expires_at
        )

        assert refresh_token_vo.jti == jti
        assert refresh_token_vo.refresh_token == token
        assert refresh_token_vo.user_id == user_id
        assert refresh_token_vo.expires_at == expires_at

    @pytest.mark.parametrize("refresh_token", ["", " ", None])
    def test_should_raise_exception_when_refresh_token_is_invalid(
        self, faker: Faker, refresh_token: str | None
    ) -> None:
        """Test that the RefreshTokenVO raises an InvalidRefreshTokenException.

        when the refresh token is invalid.
        """
        with pytest.raises(InvalidRefreshTokenException):
            RefreshTokenVO(
                refresh_token=refresh_token,  # type: ignore
                jti=UUID(faker.uuid4()),
                user_id=UUID(faker.uuid4()),
                expires_at=faker.future_datetime(tzinfo=UTC),
            )

    @pytest.mark.parametrize("jti", ["", "123", 123, "abc-123", None])
    def test_should_raise_exception_when_jti_is_invalid(
        self, faker: Faker, token: str, jti: str | int | None
    ) -> None:
        """Test that the RefreshTokenVO raises an InvalidRefreshTokenException.

        when the jti is invalid.
        """
        with pytest.raises(InvalidRefreshTokenException):
            RefreshTokenVO(
                refresh_token=token,
                jti=jti,  # type: ignore
                user_id=UUID(faker.uuid4()),
                expires_at=faker.future_datetime(tzinfo=UTC),
            )

    @pytest.mark.parametrize("user_id", ["", "123", 123, "abc-123", None])
    def test_should_raise_exception_when_user_id_is_invalid(
        self, faker: Faker, token: str, user_id: str | int | None
    ) -> None:
        """Test that the RefreshTokenVO raises an InvalidRefreshTokenException.

        when the user ID is invalid.
        """
        with pytest.raises(InvalidRefreshTokenException):
            RefreshTokenVO(
                refresh_token=token,
                jti=UUID(faker.uuid4()),
                user_id=user_id,  # type: ignore
                expires_at=faker.future_datetime(tzinfo=UTC),
            )

    def test_should_raise_exception_when_expiration_date_is_in_the_past(
        self, faker: Faker, token: str
    ) -> None:
        """Test that the RefreshTokenVO raises an InvalidRefreshTokenException.

        when the expiration date is in the past.
        """
        with pytest.raises(InvalidRefreshTokenException):
            RefreshTokenVO(
                refresh_token=token,
                jti=UUID(faker.uuid4()),
                user_id=UUID(faker.uuid4()),
                expires_at=faker.past_datetime(tzinfo=UTC),
            )
