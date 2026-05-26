from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseNameException,
)
from src.modules.warehouses.domain.value_objects.warehouse_name_vo import (
    WarehouseNameVO,
)


class TestWarehouseNameVO:
    def test_should_return_name_as_string_when_valid_name_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseNameVO returns the name as a string when a valid name is provided."""
        name = faker.company()
        name_vo = WarehouseNameVO(name)

        assert str(name_vo) == name

    def test_should_raise_exception_when_name_is_empty(self) -> None:
        """Test that the WarehouseNameVO raises an InvalidWarehouseNameException.

        when an empty name is provided.
        """
        with pytest.raises(InvalidWarehouseNameException):
            WarehouseNameVO("")

    def test_should_raise_exception_when_name_is_only_whitespace(self) -> None:
        """Test that the WarehouseNameVO raises an InvalidWarehouseNameException.

        when the name is only whitespace.
        """
        with pytest.raises(InvalidWarehouseNameException):
            WarehouseNameVO("   ")

    @pytest.mark.parametrize("name", ["a", "ab"])
    def test_should_raise_exception_when_name_is_too_short(self, name: str) -> None:
        """Test that the WarehouseNameVO raises an InvalidWarehouseNameException.

        when the name is shorter than 3 characters.
        """
        with pytest.raises(InvalidWarehouseNameException):
            WarehouseNameVO(name)

    def test_should_raise_exception_when_name_exceeds_max_length(self) -> None:
        """Test that the WarehouseNameVO raises an InvalidWarehouseNameException.

        when the name is 100 or more characters.
        """
        with pytest.raises(InvalidWarehouseNameException):
            WarehouseNameVO("a" * 100)

    def test_should_create_name_vo_when_name_is_exactly_min_length(self) -> None:
        """Test that the WarehouseNameVO is created successfully.

        when the name is exactly 3 characters long.
        """
        name_vo = WarehouseNameVO("abc")

        assert str(name_vo) == "abc"

    def test_should_create_name_vo_when_name_is_exactly_below_max_length(self) -> None:
        """Test that the WarehouseNameVO is created successfully.

        when the name is exactly 99 characters long.
        """
        name = "a" * 99
        name_vo = WarehouseNameVO(name)

        assert str(name_vo) == name

    def test_should_raise_exception_when_attempting_to_modify_name(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseNameVO raises a FrozenInstanceError.

        when attempting to modify the name after creation.
        """
        name_vo = WarehouseNameVO(faker.company())

        with pytest.raises(FrozenInstanceError):
            name_vo.name = faker.company()  # type: ignore[misc]

    def test_should_return_equal_name_vos_when_names_are_identical(self) -> None:
        """Test that two WarehouseNameVO instances with the same name are considered equal."""
        name = "Central Warehouse"
        assert WarehouseNameVO(name) == WarehouseNameVO(name)

    def test_should_return_different_name_vos_when_names_differ(self) -> None:
        """Test that two WarehouseNameVO instances with different names are not considered equal."""
        assert WarehouseNameVO("Warehouse A") != WarehouseNameVO("Warehouse B")
