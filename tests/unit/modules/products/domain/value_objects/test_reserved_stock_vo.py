from dataclasses import FrozenInstanceError

import pytest

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidReservedStockException,
)
from src.modules.products.domain.value_objects.reserved_stock_vo import (
    ReservedStockVO,
)


class TestReservedStockVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_reserved_stock_vo_when_stock_is_zero(self) -> None:
        """Test that the ReservedStockVO can be created successfully when stock is zero."""
        reserved_stock = ReservedStockVO(0)

        assert reserved_stock.reserved_stock == 0

    def test_should_create_reserved_stock_vo_when_stock_is_positive(self) -> None:
        """Test that the ReservedStockVO can be created successfully when stock is positive."""
        reserved_stock = ReservedStockVO(100)

        assert reserved_stock.reserved_stock == 100

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_stock_is_none(self) -> None:
        """Test that the ReservedStockVO raises InvalidReservedStockException when stock is None."""
        with pytest.raises(InvalidReservedStockException) as exc_info:
            ReservedStockVO(None)  # type: ignore[arg-type]

        assert "Reserved stock cannot be empty." in exc_info.value.errors

    def test_should_raise_exception_when_stock_is_negative(self) -> None:
        """Test that the ReservedStockVO raises InvalidReservedStockException when stock is negative."""
        with pytest.raises(InvalidReservedStockException) as exc_info:
            ReservedStockVO(-1)

        assert "Reserved stock cannot be negative." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # value
    # ---------------------------------------------------------------------------

    def test_should_return_stock_value(self) -> None:
        """Test that value() returns the underlying stock value."""
        reserved_stock = ReservedStockVO(50)

        assert reserved_stock.value() == 50

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_stock(
        self,
    ) -> None:
        """Test that the ReservedStockVO raises FrozenInstanceError when attempting to modify stock."""
        reserved_stock = ReservedStockVO(100)

        with pytest.raises(FrozenInstanceError):
            reserved_stock.reserved_stock = 200  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_reserved_stock_vos_when_values_are_identical(
        self,
    ) -> None:
        """Test that two ReservedStockVO instances with identical values are considered equal."""
        reserved_stock_1 = ReservedStockVO(100)
        reserved_stock_2 = ReservedStockVO(100)

        assert reserved_stock_1 == reserved_stock_2

    def test_should_return_different_reserved_stock_vos_when_values_differ(
        self,
    ) -> None:
        """Test that two ReservedStockVO instances with different values are not considered equal."""
        assert ReservedStockVO(100) != ReservedStockVO(200)
