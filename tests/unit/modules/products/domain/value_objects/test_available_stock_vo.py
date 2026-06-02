from dataclasses import FrozenInstanceError

import pytest

from src.modules.products.domain.exceptions.stock_exception import (
    InvalidAvailableStockException,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)


class TestAvailableStockVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_available_stock_vo_when_stock_is_zero(self) -> None:
        """Test that the AvailableStockVO can be created successfully when stock is zero."""
        available_stock = AvailableStockVO(0)

        assert available_stock.available_stock == 0

    def test_should_create_available_stock_vo_when_stock_is_positive(self) -> None:
        """Test that the AvailableStockVO can be created successfully when stock is positive."""
        available_stock = AvailableStockVO(100)

        assert available_stock.available_stock == 100

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_stock_is_none(self) -> None:
        """Test that the AvailableStockVO raises InvalidAvailableStockException when stock is None."""
        with pytest.raises(InvalidAvailableStockException) as exc_info:
            AvailableStockVO(None)  # type: ignore[arg-type]

        assert "Available stock cannot be empty." in exc_info.value.errors

    def test_should_raise_exception_when_stock_is_negative(self) -> None:
        """Test that the AvailableStockVO raises InvalidAvailableStockException when stock is negative."""
        with pytest.raises(InvalidAvailableStockException) as exc_info:
            AvailableStockVO(-1)

        assert "Available stock cannot be negative." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # value
    # ---------------------------------------------------------------------------

    def test_should_return_stock_value(self) -> None:
        """Test that value() returns the underlying stock value."""
        available_stock = AvailableStockVO(50)

        assert available_stock.value() == 50

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_stock(
        self,
    ) -> None:
        """Test that the AvailableStockVO raises FrozenInstanceError when attempting to modify stock."""
        available_stock = AvailableStockVO(100)

        with pytest.raises(FrozenInstanceError):
            available_stock.available_stock = 200  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_available_stock_vos_when_values_are_identical(
        self,
    ) -> None:
        """Test that two AvailableStockVO instances with identical values are considered equal."""
        available_stock_1 = AvailableStockVO(100)
        available_stock_2 = AvailableStockVO(100)

        assert available_stock_1 == available_stock_2

    def test_should_return_different_available_stock_vos_when_values_differ(
        self,
    ) -> None:
        """Test that two AvailableStockVO instances with different values are not considered equal."""
        assert AvailableStockVO(100) != AvailableStockVO(200)
