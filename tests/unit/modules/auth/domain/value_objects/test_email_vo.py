from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidEmailException,
)
from src.modules.auth.domain.value_objects.email_vo import EmailVO


class TestEmailVO:
    def test_should_return_email_as_string_when_valid_email_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the EmailVO returns the email as a string when a valid email is provided."""
        email = faker.email()
        email_vo = EmailVO(email)

        assert str(email_vo) == email

    def test_should_raise_exception_when_email_is_empty(self) -> None:
        """Test that the EmailVO raises an InvalidEmailException when an empty email is provided."""
        with pytest.raises(InvalidEmailException):
            EmailVO("")

    @pytest.mark.parametrize(
        "email",
        [
            " example@pytest.com",
            "example @pytest.com",
            "example@ pytest.com",
            "example@pytest .com",
            "example@pytest. com",
            "example@pytest.com ",
        ],
    )
    def test_should_raise_exception_when_email_contains_whitespace(
        self, email: str
    ) -> None:
        """Test that the EmailVO raises an InvalidEmailException when the email contains leading, trailing, or internal whitespace."""
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "example\t@pytest.com",
            "example\n@pytest.com",
            "..example@pytest.com",
            "example..@pytest.com",
            "example@..pytest.com",
            "example@pytest..com",
            "example@pytest.com..co",
            "example@pytest..com..co",
        ],
    )
    def test_should_raise_exception_when_email_has_invalid_format(
        self, email: str
    ) -> None:
        """Test that the EmailVO raises an InvalidEmailException when the email has an invalid format.

        such as containing tabs, newlines, or consecutive dots.
        """
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    @pytest.mark.parametrize(
        "email",
        [
            "example.pytest.com",
            "examplepytest.com",
            "example@pytest",
            "example@.pytest.com",
            "example@-pytest.com",
            "@pytest.com",
        ],
    )
    def test_should_raise_exception_when_email_is_invalid(self, email: str) -> None:
        """Test that the EmailVO raises an InvalidEmailException when the email is invalid.

        such as missing the '@' symbol, having an invalid domain, or missing the local part.
        """
        with pytest.raises(InvalidEmailException):
            EmailVO(email)

    def test_should_raise_exception_when_email_exceeds_max_length(
        self, faker: Faker
    ) -> None:
        """Test that the EmailVO raises an InvalidEmailException when the email exceeds the maximum length of 255 characters."""
        with pytest.raises(InvalidEmailException):
            EmailVO(f"{faker.email() * 255}")

    @pytest.mark.parametrize(
        "email, expected_domain",
        [
            ("example@test.com", "test.com"),
            ("example@test.com.co", "test.com.co"),
            ("example@TEST.COM", "test.com"),
            ("example@TEST.COM.co", "test.com.co"),
        ],
    )
    def test_should_return_domain_when_email_is_valid(
        self, email: str, expected_domain: str
    ) -> None:
        """Test that the EmailVO returns the correct domain when a valid email is provided."""
        email_vo = EmailVO(email)

        assert email_vo.domain() == expected_domain

    def test_should_raise_exception_when_attempting_to_modify_email(
        self, faker: Faker
    ) -> None:
        """Test that the EmailVO raises a FrozenInstanceError when attempting to modify the email after creation."""
        email_vo = EmailVO(faker.email())

        with pytest.raises(FrozenInstanceError):
            email_vo.email = faker.email()  # type: ignore[misc]
