from dataclasses import FrozenInstanceError

import pytest

from src.modules.orders.domain.exceptions.order_exception import (
    InvalidQuantityException,
)
from src.modules.orders.domain.value_objects.quantity_vo import QuantityVO


class TestQuantityVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_quantity_vo_when_quantity_is_positive(self) -> None:
        """Test that QuantityVO can be created successfully when quantity is positive."""
        quantity = QuantityVO(5)

        assert quantity.quantity == 5

    def test_should_create_quantity_vo_when_quantity_is_one(self) -> None:
        """Test that QuantityVO can be created successfully when quantity is one."""
        quantity = QuantityVO(1)

        assert quantity.quantity == 1

    def test_should_create_quantity_vo_when_quantity_is_large(self) -> None:
        """Test that QuantityVO can be created successfully when quantity is a large positive number."""
        quantity = QuantityVO(999999)

        assert quantity.quantity == 999999

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_quantity_is_zero(self) -> None:
        """Test that QuantityVO raises InvalidQuantityException when quantity is zero."""
        with pytest.raises(InvalidQuantityException) as exc_info:
            QuantityVO(0)

        assert "Quantity must be greater than 0." in exc_info.value.errors
        assert exc_info.value.quantity == 0

    def test_should_raise_exception_when_quantity_is_negative(self) -> None:
        """Test that QuantityVO raises InvalidQuantityException when quantity is negative."""
        with pytest.raises(InvalidQuantityException) as exc_info:
            QuantityVO(-5)

        assert "Quantity must be greater than 0." in exc_info.value.errors
        assert exc_info.value.quantity == -5

    def test_should_raise_exception_when_quantity_is_none(self) -> None:
        """Test that QuantityVO raises TypeError when quantity is None."""
        with pytest.raises(TypeError):
            QuantityVO(None)  # type: ignore[arg-type]

    # ---------------------------------------------------------------------------
    # value
    # ---------------------------------------------------------------------------

    def test_should_return_quantity_value(self) -> None:
        """Test that value() returns the underlying quantity value."""
        quantity = QuantityVO(42)

        assert quantity.value() == 42

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_quantity(self) -> None:
        """Test that QuantityVO raises FrozenInstanceError when attempting to modify quantity."""
        quantity = QuantityVO(10)

        with pytest.raises(FrozenInstanceError):
            quantity.quantity = 20  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_quantity_vos_when_values_are_identical(self) -> None:
        """Test that two QuantityVO instances with identical values are equal."""
        quantity_1 = QuantityVO(10)
        quantity_2 = QuantityVO(10)

        assert quantity_1 == quantity_2

    def test_should_return_different_quantity_vos_when_values_differ(self) -> None:
        """Test that two QuantityVO instances with different values are not equal."""
        assert QuantityVO(10) != QuantityVO(20)

    # ---------------------------------------------------------------------------
    # hash
    # ---------------------------------------------------------------------------

    def test_should_be_hashable(self) -> None:
        """Test that QuantityVO is hashable and can be used as a dictionary key."""
        quantity = QuantityVO(10)
        dictionary = {quantity: "test_value"}

        assert dictionary[quantity] == "test_value"

    def test_should_have_same_hash_when_values_are_equal(self) -> None:
        """Test that two QuantityVO instances with the same value have the same hash."""
        quantity_1 = QuantityVO(10)
        quantity_2 = QuantityVO(10)

        assert hash(quantity_1) == hash(quantity_2)
