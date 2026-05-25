from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.exceptions.credentials_exception import (
    InvalidNameException,
)
from src.modules.auth.domain.value_objects.name_vo import NameVO


class TestNameVO:
    def test_should_return_name_as_string_when_valid_name_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the NameVO returns the name as a string when a valid name is provided."""
        name = faker.name()
        name_vo = NameVO(name)

        assert str(name_vo) == name

    def test_should_raise_exception_when_name_is_empty(self) -> None:
        """Test that the NameVO raises an InvalidNameException when an empty name is provided."""
        with pytest.raises(InvalidNameException):
            NameVO("")

    def test_should_raise_exception_when_name_exceeds_max_length(
        self, faker: Faker
    ) -> None:
        """Test that the NameVO raises an InvalidNameException when the name exceeds the maximum length of 255 characters."""
        with pytest.raises(InvalidNameException):
            NameVO(f"{faker.name() * 255}")

    @pytest.mark.parametrize("name", ["John", "John Doe John Doe Doe"])
    def test_should_raise_exception_when_name_is_invalid(self, name: str) -> None:
        """Test that the NameVO raises an InvalidNameException when the name is invalid (e.g., contains only first name or too many parts)."""
        with pytest.raises(InvalidNameException):
            NameVO(name)

    def test_should_raise_exception_when_attempting_to_modify_name(
        self, faker: Faker
    ) -> None:
        """Test that the NameVO raises a FrozenInstanceError when attempting to modify the name after creation."""
        name_vo = NameVO(faker.name())

        with pytest.raises(FrozenInstanceError):
            name_vo.name = faker.name()  # type: ignore[misc]
