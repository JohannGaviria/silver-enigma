from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.auth_exception import (
    InvalidPlainPasswordException,
)
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class TestPlainPasswordVO:
    def test_should_return_plain_password_as_string_when_valid_password_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO returns the plain password as a string when a valid password is provided."""
        plain_password = faker.password()
        plain_password_vo = PlainPasswordVO(plain_password)

        assert str(plain_password_vo) == plain_password

    def test_should_raise_exception_when_plain_password_is_empty(self) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when an empty plain password is provided."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO("")

    def test_should_raise_exception_when_plain_password_is_too_short(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when the plain password is shorter."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(length=7))

    def test_should_raise_exception_when_plain_password_is_lowercase_only(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when the plain password is lowercase only."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password().lower())

    def test_should_raise_exception_when_plain_password_is_uppercase_only(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when the plain password is uppercase only."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password().upper())

    def test_should_raise_exception_when_plain_password_has_no_digits(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when the plain password has no digits."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(digits=False))

    def test_should_raise_exception_when_plain_password_has_no_special_characters(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises an InvalidPlainPasswordException when the plain password has no special characters."""
        with pytest.raises(InvalidPlainPasswordException):
            PlainPasswordVO(faker.password(special_chars=False))

    def test_should_raise_exception_when_attempting_to_modify_plain_password(
        self, faker: Faker
    ) -> None:
        """Test that the PlainPasswordVO raises a FrozenInstanceError when attempting to modify the plain password after creation."""
        plain_password_vo = PlainPasswordVO(faker.password())

        with pytest.raises(FrozenInstanceError):
            plain_password_vo.plain_password = faker.password()  # type: ignore[misc]
