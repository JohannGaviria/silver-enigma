"""Tests for the WarehouseAddressVO value object."""

from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.warehouses.domain.exceptions.warehouse_exception import (
    InvalidWarehouseAddressException,
)
from src.modules.warehouses.domain.value_objects.warehouse_address_vo import (
    WarehouseAddressVO,
)


class TestWarehouseAddressVO:
    def test_should_return_address_as_string_when_valid_address_is_provided(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseAddressVO returns the address as a string.

        when a valid address is provided.
        """
        address = faker.address()
        address_vo = WarehouseAddressVO(address)

        assert str(address_vo) == address

    def test_should_raise_exception_when_address_is_empty(self) -> None:
        """Test that the WarehouseAddressVO raises an InvalidWarehouseAddressException.

        when an empty address is provided.
        """
        with pytest.raises(InvalidWarehouseAddressException):
            WarehouseAddressVO("")

    def test_should_raise_exception_when_address_is_only_whitespace(self) -> None:
        """Test that the WarehouseAddressVO raises an InvalidWarehouseAddressException.

        when the address is only whitespace.
        """
        with pytest.raises(InvalidWarehouseAddressException):
            WarehouseAddressVO("   ")

    @pytest.mark.parametrize("address", ["a", "ab"])
    def test_should_raise_exception_when_address_is_too_short(
        self, address: str
    ) -> None:
        """Test that the WarehouseAddressVO raises an InvalidWarehouseAddressException.

        when the address is shorter than 3 characters.
        """
        with pytest.raises(InvalidWarehouseAddressException):
            WarehouseAddressVO(address)

    def test_should_raise_exception_when_address_exceeds_max_length(self) -> None:
        """Test that the WarehouseAddressVO raises an InvalidWarehouseAddressException.

        when the address is 255 or more characters.
        """
        with pytest.raises(InvalidWarehouseAddressException):
            WarehouseAddressVO("a" * 255)

    def test_should_create_address_vo_when_address_is_exactly_min_length(self) -> None:
        """Test that the WarehouseAddressVO is created successfully.

        when the address is exactly 3 characters long.
        """
        address_vo = WarehouseAddressVO("abc")

        assert str(address_vo) == "abc"

    def test_should_create_address_vo_when_address_is_exactly_below_max_length(
        self,
    ) -> None:
        """Test that the WarehouseAddressVO is created successfully.

        when the address is exactly 254 characters long.
        """
        address = "a" * 254
        address_vo = WarehouseAddressVO(address)

        assert str(address_vo) == address

    def test_should_raise_exception_when_attempting_to_modify_address(
        self, faker: Faker
    ) -> None:
        """Test that the WarehouseAddressVO raises a FrozenInstanceError.

        when attempting to modify the address after creation.
        """
        address_vo = WarehouseAddressVO(faker.address())

        with pytest.raises(FrozenInstanceError):
            address_vo.address = faker.address()  # type: ignore[misc]

    def test_should_return_equal_address_vos_when_addresses_are_identical(self) -> None:
        """Test that two WarehouseAddressVO instances with the same address are considered equal."""
        address = "123 Main Street, Springfield"
        assert WarehouseAddressVO(address) == WarehouseAddressVO(address)

    def test_should_return_different_address_vos_when_addresses_differ(self) -> None:
        """Test that two WarehouseAddressVO instances.

        with different addresses are not considered equal.
        """
        assert WarehouseAddressVO("123 Main St") != WarehouseAddressVO("456 Oak Ave")
